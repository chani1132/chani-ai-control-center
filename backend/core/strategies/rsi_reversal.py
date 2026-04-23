import logging
from typing import Optional

import pandas as pd
import pandas_ta as ta

from core.strategies.base import BaseStrategy, Signal

logger = logging.getLogger(__name__)


class Strategy(BaseStrategy):
    """
    RSI 역추세 전략 (현물)

    - RSI < oversold  → 매수
    - RSI > overbought → 매도 (보유 중일 때)

    config 예시:
    {
        "timeframe": "1h",
        "rsi_period": 14,
        "oversold": 30,
        "overbought": 70,
        "risk_pct": 0.1,        # 잔고의 10% 사용
        "interval_seconds": 60
    }
    """

    name = "rsi_reversal"
    description = "RSI 역추세 전략 - 과매도 매수 / 과매수 매도"

    def __init__(self, config: dict):
        super().__init__(config)
        self.timeframe = config.get("timeframe", "1h")
        self.rsi_period = config.get("rsi_period", 14)
        self.oversold = config.get("oversold", 30)
        self.overbought = config.get("overbought", 70)
        self.risk_pct = config.get("risk_pct", 0.1)
        self._in_position = False

    async def on_start(self, exchange, symbol: str):
        logger.info(f"[RSI Reversal] 시작 - {symbol} / {self.timeframe}")
        self._in_position = False

    async def on_stop(self, exchange, symbol: str):
        logger.info(f"[RSI Reversal] 종료 - {symbol}")

    async def analyze(self, exchange, symbol: str) -> Optional[Signal]:
        try:
            ohlcv = await exchange._client.fetch_ohlcv(
                symbol, self.timeframe, limit=self.rsi_period + 10
            )
        except Exception as e:
            logger.error(f"[RSI Reversal] OHLCV 조회 실패: {e}")
            return None

        df = pd.DataFrame(ohlcv, columns=["ts", "open", "high", "low", "close", "volume"])
        df["rsi"] = ta.rsi(df["close"], length=self.rsi_period)

        if df["rsi"].isna().all():
            return None

        rsi = df["rsi"].iloc[-1]
        price = df["close"].iloc[-1]

        logger.info(f"[RSI Reversal] {symbol} | RSI={rsi:.1f} | 가격={price:,.4f}")

        # 매수 조건: RSI 과매도 + 미보유
        if rsi < self.oversold and not self._in_position:
            amount = await self._calc_amount(exchange, symbol, price)
            if amount <= 0:
                return None
            self._in_position = True
            return Signal(
                action="buy",
                symbol=symbol,
                price=price,
                amount=amount,
                reason=f"RSI 과매도 ({rsi:.1f})",
                metadata={"strategy": self.name, "rsi": rsi},
            )

        # 매도 조건: RSI 과매수 + 보유 중
        if rsi > self.overbought and self._in_position:
            amount = await self._get_position_amount(exchange, symbol)
            if amount <= 0:
                return None
            self._in_position = False
            return Signal(
                action="sell",
                symbol=symbol,
                price=price,
                amount=amount,
                reason=f"RSI 과매수 ({rsi:.1f})",
                metadata={"strategy": self.name, "rsi": rsi},
            )

        return None

    async def _calc_amount(self, exchange, symbol: str, price: float) -> float:
        try:
            balances = await exchange.get_balance()
            quote = symbol.split("/")[1]  # BTC/USDT → USDT
            for b in balances:
                if b.currency == quote:
                    usable = b.free * self.risk_pct
                    return round(usable / price, 6)
        except Exception as e:
            logger.error(f"잔고 조회 실패: {e}")
        return 0.0

    async def _get_position_amount(self, exchange, symbol: str) -> float:
        try:
            balances = await exchange.get_balance()
            base = symbol.split("/")[0]  # BTC/USDT → BTC
            for b in balances:
                if b.currency == base:
                    return round(b.free * 0.99, 6)  # 수수료 여유
        except Exception as e:
            logger.error(f"잔고 조회 실패: {e}")
        return 0.0
