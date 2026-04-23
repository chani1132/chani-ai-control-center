from fastapi import APIRouter
from api.routes.bot import router as bot_router
from api.routes.trades import router as trades_router
from api.routes.exchange import router as exchange_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(bot_router)
api_router.include_router(trades_router)
api_router.include_router(exchange_router)
