import ccxt.async_support as ccxt
from typing import Optional
from core.exchanges.base import BaseExchange, Balance, Ticker, Order


class UpbitExchange(BaseExchange):
    def __init__(self, api_key: str, secret_key: str):
        super().__init__(api_key, secret_key)
        self._client = ccxt.upbit({
            "apiKey": api_key,
            "secret": secret_key,
            "enableRateLimit": True,
        })

    async def ping(self) -> bool:
        try:
            await self._client.fetch_status()
            return True
        except Exception:
            return False

    async def get_balance(self) -> list[Balance]:
        raw = await self._client.fetch_balance()
        result = []
        for currency, info in raw.get("info", {}).items():
            if isinstance(info, dict):
                total = float(info.get("balance", 0)) + float(info.get("locked", 0))
                if total > 0:
                    result.append(Balance(
                        currency=currency,
                        free=float(info.get("balance", 0)),
                        used=float(info.get("locked", 0)),
                        total=total,
                    ))
        return result

    async def get_ticker(self, symbol: str) -> Ticker:
        raw = await self._client.fetch_ticker(symbol)
        return Ticker(
            symbol=symbol,
            last=raw["last"],
            bid=raw["bid"],
            ask=raw["ask"],
            volume=raw["baseVolume"],
            change_pct=raw.get("percentage", 0.0) or 0.0,
        )

    async def create_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        order_type: str = "market",
    ) -> Order:
        raw = await self._client.create_order(symbol, order_type, side, amount, price)
        return Order(
            order_id=raw["id"],
            symbol=symbol,
            side=side,
            price=raw.get("price") or price or 0.0,
            amount=raw.get("amount", amount),
            cost=raw.get("cost", 0.0),
            status=raw.get("status", "open"),
            timestamp=raw.get("timestamp", 0),
        )

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        try:
            await self._client.cancel_order(order_id, symbol)
            return True
        except Exception:
            return False

    async def get_open_orders(self, symbol: Optional[str] = None) -> list[Order]:
        raw_orders = await self._client.fetch_open_orders(symbol)
        return [
            Order(
                order_id=o["id"],
                symbol=o["symbol"],
                side=o["side"],
                price=o.get("price") or 0.0,
                amount=o.get("amount", 0.0),
                cost=o.get("cost", 0.0),
                status=o.get("status", "open"),
                timestamp=o.get("timestamp", 0),
            )
            for o in raw_orders
        ]

    async def close(self):
        await self._client.close()
