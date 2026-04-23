import asyncio
import importlib
import json
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from core.exchanges.upbit import UpbitExchange
from core.exchanges.okx import OkxExchange
from core.notifications.telegram import notifier
from database.db import AsyncSessionLocal
from database.models import BotState, Trade

logger = logging.getLogger(__name__)


class BotManager:
    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._tasks: dict[str, asyncio.Task] = {}
        self._exchanges: dict[str, UpbitExchange | OkxExchange] = {}

    def _build_exchange(self, exchange_id: str):
        if exchange_id == "upbit":
            return UpbitExchange(settings.upbit_access_key, settings.upbit_secret_key)
        if exchange_id == "okx":
            return OkxExchange(settings.okx_api_key, settings.okx_secret_key, settings.okx_passphrase)
        raise ValueError(f"Unknown exchange: {exchange_id}")

    def _load_strategy(self, strategy_name: str, config: dict):
        module = importlib.import_module(f"core.strategies.{strategy_name}")
        cls = getattr(module, "Strategy")
        return cls(config)

    async def start(self, exchange_id: str, strategy_name: str, symbol: str, config: dict) -> bool:
        if exchange_id in self._tasks and not self._tasks[exchange_id].done():
            logger.warning(f"Bot already running for {exchange_id}")
            return False

        exchange = self._build_exchange(exchange_id)
        self._exchanges[exchange_id] = exchange

        strategy = self._load_strategy(strategy_name, config)
        await strategy.on_start(exchange, symbol)

        task = asyncio.create_task(self._run_loop(exchange_id, exchange, strategy, symbol))
        self._tasks[exchange_id] = task

        async with AsyncSessionLocal() as db:
            await self._upsert_bot_state(db, exchange_id, True, strategy_name, symbol, config)

        await notifier.send_bot_status(exchange_id, "started", strategy_name)
        logger.info(f"Bot started: {exchange_id} / {strategy_name} / {symbol}")
        return True

    async def stop(self, exchange_id: str) -> bool:
        task = self._tasks.get(exchange_id)
        if not task or task.done():
            return False

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        exchange = self._exchanges.pop(exchange_id, None)
        if exchange:
            await exchange.close()

        async with AsyncSessionLocal() as db:
            await db.execute(
                update(BotState)
                .where(BotState.exchange == exchange_id)
                .values(is_running=False, updated_at=datetime.utcnow())
            )
            await db.commit()

        await notifier.send_bot_status(exchange_id, "stopped")
        logger.info(f"Bot stopped: {exchange_id}")
        return True

    async def _run_loop(self, exchange_id: str, exchange, strategy, symbol: str):
        interval = strategy.config.get("interval_seconds", 60)
        try:
            while True:
                try:
                    signal = await strategy.analyze(exchange, symbol)
                    if signal and signal.action != "hold":
                        await self._execute_signal(exchange_id, exchange, signal)
                except Exception as e:
                    logger.error(f"Strategy error [{exchange_id}]: {e}")
                    await notifier.send_error(exchange_id, str(e))
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            await strategy.on_stop(exchange, symbol)

    async def _execute_signal(self, exchange_id: str, exchange, signal):
        order = await exchange.create_order(
            symbol=signal.symbol,
            side=signal.action,
            amount=signal.amount,
            price=signal.price if signal.action not in ("market",) else None,
        )
        async with AsyncSessionLocal() as db:
            trade = Trade(
                exchange=exchange_id,
                market_type="spot" if exchange_id == "upbit" else "futures",
                symbol=signal.symbol,
                side=signal.action,
                price=order.price,
                amount=order.amount,
                cost=order.cost,
                strategy=signal.metadata.get("strategy", "unknown"),
                order_id=order.order_id,
            )
            db.add(trade)
            await db.commit()

        await notifier.send_trade(exchange_id, signal.action, signal.symbol, order.price, order.amount)

    async def _upsert_bot_state(self, db: AsyncSession, exchange_id, running, strategy, symbol, config):
        existing = await db.scalar(select(BotState).where(BotState.exchange == exchange_id))
        if existing:
            existing.is_running = running
            existing.strategy = strategy
            existing.symbol = symbol
            existing.config = json.dumps(config)
            existing.updated_at = datetime.utcnow()
        else:
            db.add(BotState(
                exchange=exchange_id,
                is_running=running,
                strategy=strategy,
                symbol=symbol,
                config=json.dumps(config),
            ))
        await db.commit()

    def get_status(self, exchange_id: str) -> dict:
        task = self._tasks.get(exchange_id)
        return {
            "exchange": exchange_id,
            "running": bool(task and not task.done()),
        }


bot_manager = BotManager()
