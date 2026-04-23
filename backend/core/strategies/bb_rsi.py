import logging
from typing import Optional

import pandas as pd
import pandas_ta as ta

from core.strategies.base import BaseStrategy, Signal

logger = logging.getLogger(__name__)


class Strategy(BaseStrategy):
    """
    볼린저밴드(2σ/4σ) + RSI 복합 전략 (선물)

    진입 조건 (2단계):
      일반 롱:  가격 < BB하단(2σ)  AND  RSI < rsi_oversold
      강한 롱:  가격 < BB하단(4σ)  AND  RSI < rsi_extreme_oversold  → 추가 진입
      일반 숏:  가격 > BB상단(2σ)  AND  RSI > rsi_overbought
      강한 숏:  가격 > BB상단(4σ)  AND  RSI > rsi_extreme_overbought → 추가 진입

    청산 조건:
      롱 포지션: 가격 >= BB중심선(2σ)  OR  RSI > 55
      숏 포지션: 가격 <= BB중심선(2σ)  OR  RSI < 45

    config 예시:
    {
        "timeframe": "1h",
        "bb_period": 20,
        "bb_std1": 2,
        "bb_std2": 4,
        "rsi_period": 14,
        "rsi_oversold": 35,
        "rsi_overbought": 65,
        "rsi_extreme_oversold": 20,
        "rsi_extreme_overbought": 80,
        "leverage": 5,
        "risk_pct": 0.05,
        "add_pct": 0.03,
        "interval_seconds": 60
    }
    """

    name = "bb_rsi"
    description = "볼린저밴드(2σ/4σ) + RSI 복합 전략 - 2단계 진입, 중심선 청산"

    def __init__(self, config: dict):
        super().__init__(config)
        self.timeframe = config.get("timeframe", "1h")
        self.bb_period = config.get("bb_period", 20)
        self.bb_std1 = config.get("bb_std1", 2)
        self.bb_std2 = config.get("bb_std2", 4)
        self.rsi_period = config.get("rsi_period", 14)
        self.rsi_oversold = config.get("rsi_oversold", 35)
        self.rsi_overbought = config.get("rsi_overbought", 65)
        self.rsi_extreme_ov = config.get("rsi_extreme_oversold", 20)
        self.rsi_extreme_ob = config.get("rsi_extreme_overbought", 80)
        self.leverage = config.get("leverage", 5)
        self.risk_pct = config.get("risk_pct", 0.05)
        self.add_pct = config.get("add_pct", 0.03)  # 추가 진입 비율

        # 포지션 상태
        self._position: Optional[str] = None  # "long" | "short" | None
        self._added = False  # 4σ 추가 진입 여부

    async def on_start(self, exchange, symbol: str):
        logger.info(f"[BB+RSI] 시작 - {symbol} / {self.timeframe}")
        await exchange.set_leverage(symbol, self.leverage)
        self._position = None
        self._added = False

    async def on_stop(self, exchange, symbol: str):
        logger.info(f"[BB+RSI] 종료 - {symbol}")

    async def analyze(self, exchange, symbol: str) -> Optional[Signal]:
        try:
            limit = self.bb_period + 20
            ohlcv = await exchange._client.fetch_ohlcv(symbol, self.timeframe, limit=limit)
        except Exception as e:
            logger.error(f"[BB+RSI] OHLCV 조회 실패: {e}")
            return None

        df = pd.DataFrame(ohlcv, columns=["ts", "open", "high", "low", "close", "volume"])

        # 지표 계산
        bb2 = ta.bbands(df["close"], length=self.bb_period, std=self.bb_std1)
        bb4 = ta.bbands(df["close"], length=self.bb_period, std=self.bb_std2)
        df["rsi"] = ta.rsi(df["close"], length=self.rsi_period)

        if bb2 is None or bb4 is None or df["rsi"].isna().all():
            return None

        lower2_col = f"BBL_{self.bb_period}_{float(self.bb_std1)}"
        upper2_col = f"BBU_{self.bb_period}_{float(self.bb_std1)}"
        mid2_col   = f"BBM_{self.bb_period}_{float(self.bb_std1)}"
        lower4_col = f"BBL_{self.bb_period}_{float(self.bb_std2)}"
        upper4_col = f"BBU_{self.bb_period}_{float(self.bb_std2)}"

        price   = df["close"].iloc[-1]
        rsi     = df["rsi"].iloc[-1]
        lower2  = bb2[lower2_col].iloc[-1]
        upper2  = bb2[upper2_col].iloc[-1]
        mid2    = bb2[mid2_col].iloc[-1]
        lower4  = bb4[lower4_col].iloc[-1]
        upper4  = bb4[upper4_col].iloc[-1]

        logger.info(
            f"[BB+RSI] {symbol} | RSI={rsi:.1f} | 가격={price:,.4f} | "
            f"BB2=[{lower2:,.4f}~{upper2:,.4f}] | BB4=[{lower4:,.4f}~{upper4:,.4f}] | "
            f"포지션={self._position}"
        )

        # ── 청산 ──────────────────────────────────────────────
        if self._position == "long" and (price >= mid2 or rsi > 55):
            amount = await self._get_position_contracts(exchange, symbol)
            if amount > 0:
                self._position = None
                self._added = False
                return Signal(
                    action="sell",
                    symbol=symbol,
                    price=price,
                    amount=amount,
                    reason=f"롱 청산 (가격={price:,.4f}, RSI={rsi:.1f})",
                    metadata={"strategy": self.name, "rsi": rsi, "reduce_only": True},
                )

        if self._position == "short" and (price <= mid2 or rsi < 45):
            amount = await self._get_position_contracts(exchange, symbol)
            if amount > 0:
                self._position = None
                self._added = False
                return Signal(
                    action="buy",
                    symbol=symbol,
                    price=price,
                    amount=amount,
                    reason=f"숏 청산 (가격={price:,.4f}, RSI={rsi:.1f})",
                    metadata={"strategy": self.name, "rsi": rsi, "reduce_only": True},
                )

        # ── 4σ 추가 진입 ──────────────────────────────────────
        if self._position == "long" and not self._added and price < lower4 and rsi < self.rsi_extreme_ov:
            amount = await self._calc_contracts(exchange, symbol, price, self.add_pct)
            if amount > 0:
                self._added = True
                return Signal(
                    action="buy",
                    symbol=symbol,
                    price=price,
                    amount=amount,
                    reason=f"롱 추가진입 4σ (RSI={rsi:.1f})",
                    metadata={"strategy": self.name, "rsi": rsi, "entry": "4sigma_add"},
                )

        if self._position == "short" and not self._added and price > upper4 and rsi > self.rsi_extreme_ob:
            amount = await self._calc_contracts(exchange, symbol, price, self.add_pct)
            if amount > 0:
                self._added = True
                return Signal(
                    action="sell",
                    symbol=symbol,
                    price=price,
                    amount=amount,
                    reason=f"숏 추가진입 4σ (RSI={rsi:.1f})",
                    metadata={"strategy": self.name, "rsi": rsi, "entry": "4sigma_add"},
                )

        # ── 신규 진입 (2σ) ────────────────────────────────────
        if self._position is None:
            if price < lower2 and rsi < self.rsi_oversold:
                amount = await self._calc_contracts(exchange, symbol, price, self.risk_pct)
                if amount > 0:
                    self._position = "long"
                    self._added = False
                    return Signal(
                        action="buy",
                        symbol=symbol,
                        price=price,
                        amount=amount,
                        reason=f"롱 진입 2σ (RSI={rsi:.1f})",
                        metadata={"strategy": self.name, "rsi": rsi, "entry": "2sigma"},
                    )

            if price > upper2 and rsi > self.rsi_overbought:
                amount = await self._calc_contracts(exchange, symbol, price, self.risk_pct)
                if amount > 0:
                    self._position = "short"
                    self._added = False
                    return Signal(
                        action="sell",
                        symbol=symbol,
                        price=price,
                        amount=amount,
                        reason=f"숏 진입 2σ (RSI={rsi:.1f})",
                        metadata={"strategy": self.name, "rsi": rsi, "entry": "2sigma"},
                    )

        return None

    async def _calc_contracts(self, exchange, symbol: str, price: float, pct: float) -> float:
        try:
            balances = await exchange.get_balance()
            for b in balances:
                if b.currency in ("USDT", "BUSD", "USDC"):
                    usable = b.free * pct * self.leverage
                    return round(usable / price, 4)
        except Exception as e:
            logger.error(f"잔고 조회 실패: {e}")
        return 0.0

    async def _get_position_contracts(self, exchange, symbol: str) -> float:
        try:
            positions = await exchange.get_positions()
            for p in positions:
                if p["symbol"] == symbol:
                    return abs(float(p["contracts"]))
        except Exception as e:
            logger.error(f"포지션 조회 실패: {e}")
        return 0.0
