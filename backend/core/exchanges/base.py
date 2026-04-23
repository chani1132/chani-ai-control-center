from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class Balance:
    currency: str
    free: float
    used: float
    total: float


@dataclass
class Ticker:
    symbol: str
    last: float
    bid: float
    ask: float
    volume: float
    change_pct: float


@dataclass
class Order:
    order_id: str
    symbol: str
    side: str
    price: float
    amount: float
    cost: float
    status: str
    timestamp: int


class BaseExchange(ABC):
    def __init__(self, api_key: str, secret_key: str, **kwargs):
        self.api_key = api_key
        self.secret_key = secret_key

    @abstractmethod
    async def get_balance(self) -> list[Balance]:
        ...

    @abstractmethod
    async def get_ticker(self, symbol: str) -> Ticker:
        ...

    @abstractmethod
    async def create_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        order_type: str = "market",
    ) -> Order:
        ...

    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        ...

    @abstractmethod
    async def get_open_orders(self, symbol: Optional[str] = None) -> list[Order]:
        ...

    @abstractmethod
    async def ping(self) -> bool:
        ...
