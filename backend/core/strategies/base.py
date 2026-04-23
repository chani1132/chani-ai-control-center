from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Signal:
    action: str          # buy | sell | long | short | close | hold
    symbol: str
    price: float
    amount: float
    reason: str = ""
    metadata: dict = field(default_factory=dict)


class BaseStrategy(ABC):
    name: str = "base"
    description: str = ""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    async def analyze(self, exchange, symbol: str) -> Optional[Signal]:
        """분석 후 매매 신호 반환. 없으면 None."""
        ...

    @abstractmethod
    async def on_start(self, exchange, symbol: str):
        """봇 시작 시 초기화."""
        ...

    @abstractmethod
    async def on_stop(self, exchange, symbol: str):
        """봇 종료 시 정리."""
        ...
