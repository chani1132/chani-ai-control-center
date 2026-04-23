from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.bot_manager import bot_manager

router = APIRouter(prefix="/bot", tags=["bot"])


class StartRequest(BaseModel):
    exchange: str
    strategy: str
    symbol: str
    config: dict = {}


@router.post("/start")
async def start_bot(req: StartRequest):
    ok = await bot_manager.start(req.exchange, req.strategy, req.symbol, req.config)
    if not ok:
        raise HTTPException(400, detail=f"Bot already running for {req.exchange}")
    return {"status": "started", "exchange": req.exchange}


@router.post("/stop/{exchange}")
async def stop_bot(exchange: str):
    ok = await bot_manager.stop(exchange)
    if not ok:
        raise HTTPException(400, detail=f"Bot not running for {exchange}")
    return {"status": "stopped", "exchange": exchange}


@router.get("/status/{exchange}")
async def bot_status(exchange: str):
    return bot_manager.get_status(exchange)


@router.get("/status")
async def all_status():
    return {
        "upbit": bot_manager.get_status("upbit"),
        "okx": bot_manager.get_status("okx"),
    }
