from datetime import datetime
from sqlalchemy import String, Float, DateTime, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from database.db import Base


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exchange: Mapped[str] = mapped_column(String(20))       # upbit | okx
    market_type: Mapped[str] = mapped_column(String(10))    # spot | futures
    symbol: Mapped[str] = mapped_column(String(30))
    side: Mapped[str] = mapped_column(String(10))           # buy | sell | long | short
    price: Mapped[float] = mapped_column(Float)
    amount: Mapped[float] = mapped_column(Float)
    cost: Mapped[float] = mapped_column(Float)
    fee: Mapped[float] = mapped_column(Float, default=0.0)
    pnl: Mapped[float] = mapped_column(Float, default=0.0)
    strategy: Mapped[str] = mapped_column(String(50), default="manual")
    order_id: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[str] = mapped_column(String(20), default="filled")  # open | filled | cancelled
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BotState(Base):
    __tablename__ = "bot_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exchange: Mapped[str] = mapped_column(String(20), unique=True)
    is_running: Mapped[bool] = mapped_column(Boolean, default=False)
    strategy: Mapped[str] = mapped_column(String(50), default="")
    symbol: Mapped[str] = mapped_column(String(30), default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    config: Mapped[str] = mapped_column(Text, default="{}")  # JSON
