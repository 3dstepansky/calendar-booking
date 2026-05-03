import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    async def send_booking_notification(self, chat_id: str, message: str):
        """
        Отправка уведомления о новом бронировании.
        """
        if not self.token or self.token == "your_bot_token":
            logger.warning("TELEGRAM_BOT_TOKEN не настроен. Пропускаю отправку уведомления.")
            return

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления в Telegram: {e}")
                return None
