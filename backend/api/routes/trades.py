from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from database.models import Trade

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("")
async def list_trades(
    exchange: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    q = select(Trade).order_by(desc(Trade.created_at)).limit(limit).offset(offset)
    if exchange:
        q = q.where(Trade.exchange == exchange)
    result = await db.execute(q)
    trades = result.scalars().all()
    return [
        {
            "id": t.id,
            "exchange": t.exchange,
            "market_type": t.market_type,
            "symbol": t.symbol,
            "side": t.side,
            "price": t.price,
            "amount": t.amount,
            "cost": t.cost,
            "fee": t.fee,
            "pnl": t.pnl,
            "strategy": t.strategy,
            "status": t.status,
            "created_at": t.created_at.isoformat(),
        }
        for t in trades
    ]


@router.get("/summary")
async def trade_summary(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trade))
    trades = result.scalars().all()
    total_pnl = sum(t.pnl for t in trades)
    total_trades = len(trades)
    wins = sum(1 for t in trades if t.pnl > 0)
    return {
        "total_trades": total_trades,
        "total_pnl": round(total_pnl, 4),
        "win_count": wins,
        "loss_count": total_trades - wins,
        "win_rate": round(wins / total_trades * 100, 1) if total_trades else 0,
    }
