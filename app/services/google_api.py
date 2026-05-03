import httpx
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import OAuthToken
from app.core.config import settings

class GoogleCalendarService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_valid_token(self, user_id: int) -> str:
        """
        Проверяет, живой ли токен. Если истек — обновляет его через refresh_token.
        """
        result = await self.db.execute(
            select(OAuthToken).where(OAuthToken.user_id == user_id)
        )
        token_record = result.scalar_one_or_none()

        if not token_record:
            raise Exception("Токены Google не найдены. Нужно заново авторизоваться.")

        # Если до истечения осталось меньше 5 минут — обновляем
        if datetime.utcnow() + timedelta(minutes=5) >= token_record.expires_at:
            await self._refresh_token(token_record)

        return token_record.access_token

    async def _refresh_token(self, token_record: OAuthToken):
        """Обмен refresh_token на новый access_token"""
        if not token_record.refresh_token:
            raise Exception("Refresh token отсутствует. Нужно заново пройти OAuth с параметром access_type=offline.")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "refresh_token": token_record.refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            
        if response.status_code != 200:
            raise Exception(f"Не удалось обновить токен Google: {response.text}")

        data = response.json()
        token_record.access_token = data["access_token"]
        token_record.expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])
        
        await self.db.commit()

    async def get_freebusy(self, user_id: int, start_time: datetime, end_time: datetime):
        """
        Запрашивает у Google периоды занятости организатора.
        """
        token = await self.get_valid_token(user_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.googleapis.com/calendar/v3/freeBusy",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "timeMin": start_time.isoformat() + "Z",
                    "timeMax": end_time.isoformat() + "Z",
                    "items": [{"id": "primary"}]
                }
            )

        if response.status_code != 200:
            raise Exception(f"Ошибка Google Freebusy: {response.text}")

        return response.json().get("calendars", {}).get("primary", {}).get("busy", [])

    async def create_event(self, user_id: int, summary: str, start_time: datetime, end_time: datetime, guest_email: str):
        """
        Создает реальное событие в календаре Google.
        """
        token = await self.get_valid_token(user_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "summary": summary,
                    "start": {"dateTime": start_time.isoformat() + "Z"},
                    "end": {"dateTime": end_time.isoformat() + "Z"},
                    "attendees": [{"email": guest_email}]
                }
            )

        if response.status_code != 200:
            raise Exception(f"Не удалось создать событие в Google: {response.text}")

        return response.json()
