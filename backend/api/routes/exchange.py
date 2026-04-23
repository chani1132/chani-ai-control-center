from fastapi import APIRouter, HTTPException
from config.settings import settings
from core.exchanges.upbit import UpbitExchange
from core.exchanges.okx import OkxExchange

router = APIRouter(prefix="/exchange", tags=["exchange"])


@router.get("/upbit/balance")
async def upbit_balance():
    ex = UpbitExchange(settings.upbit_access_key, settings.upbit_secret_key)
    try:
        balances = await ex.get_balance()
        return [{"currency": b.currency, "free": b.free, "used": b.used, "total": b.total} for b in balances]
    finally:
        await ex.close()


@router.get("/upbit/ticker/{symbol:path}")
async def upbit_ticker(symbol: str):
    ex = UpbitExchange(settings.upbit_access_key, settings.upbit_secret_key)
    try:
        ticker = await ex.get_ticker(symbol)
        return {"symbol": ticker.symbol, "last": ticker.last, "bid": ticker.bid, "ask": ticker.ask, "change_pct": ticker.change_pct}
    finally:
        await ex.close()


@router.get("/okx/balance")
async def okx_balance():
    ex = OkxExchange(settings.okx_api_key, settings.okx_secret_key, settings.okx_passphrase)
    try:
        balances = await ex.get_balance()
        return [{"currency": b.currency, "free": b.free, "used": b.used, "total": b.total} for b in balances]
    finally:
        await ex.close()


@router.get("/okx/positions")
async def okx_positions():
    ex = OkxExchange(settings.okx_api_key, settings.okx_secret_key, settings.okx_passphrase)
    try:
        return await ex.get_positions()
    finally:
        await ex.close()


@router.get("/okx/ticker/{symbol:path}")
async def okx_ticker(symbol: str):
    ex = OkxExchange(settings.okx_api_key, settings.okx_secret_key, settings.okx_passphrase)
    try:
        ticker = await ex.get_ticker(symbol)
        return {"symbol": ticker.symbol, "last": ticker.last, "bid": ticker.bid, "ask": ticker.ask, "change_pct": ticker.change_pct}
    finally:
        await ex.close()


@router.get("/ping")
async def ping_exchanges():
    upbit = UpbitExchange(settings.upbit_access_key, settings.upbit_secret_key)
    okx = OkxExchange(settings.okx_api_key, settings.okx_secret_key, settings.okx_passphrase)
    try:
        upbit_ok = await upbit.ping()
        okx_ok = await okx.ping()
        return {"upbit": upbit_ok, "okx": okx_ok}
    finally:
        await upbit.close()
        await okx.close()
