import logging
from telegram import Bot
from telegram.error import TelegramError
from config.settings import settings

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self):
        self._bot: Bot | None = None
        self._chat_id = settings.telegram_chat_id

    def _get_bot(self) -> Bot | None:
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            return None
        if self._bot is None:
            self._bot = Bot(token=settings.telegram_bot_token)
        return self._bot

    async def send(self, message: str) -> bool:
        bot = self._get_bot()
        if not bot:
            logger.warning("Telegram not configured, skipping notification.")
            return False
        try:
            await bot.send_message(
                chat_id=self._chat_id,
                text=message,
                parse_mode="HTML",
            )
            return True
        except TelegramError as e:
            logger.error(f"Telegram send failed: {e}")
            return False

    async def send_trade(self, exchange: str, side: str, symbol: str, price: float, amount: float, pnl: float = 0.0):
        side_emoji = "🟢" if side in ("buy", "long") else "🔴"
        pnl_str = f"\nPnL: <b>{pnl:+.4f}</b>" if pnl else ""
        msg = (
            f"{side_emoji} <b>[{exchange.upper()}] {side.upper()}</b>\n"
            f"심볼: {symbol}\n"
            f"가격: {price:,.4f}\n"
            f"수량: {amount}"
            f"{pnl_str}"
        )
        await self.send(msg)

    async def send_bot_status(self, exchange: str, status: str, strategy: str = ""):
        emoji = "▶️" if status == "started" else "⏹️"
        strategy_str = f" ({strategy})" if strategy else ""
        await self.send(f"{emoji} <b>[{exchange.upper()}]</b> 봇 {status}{strategy_str}")

    async def send_error(self, exchange: str, error: str):
        await self.send(f"⚠️ <b>[{exchange.upper()}] 오류</b>\n{error}")


notifier = TelegramNotifier()
