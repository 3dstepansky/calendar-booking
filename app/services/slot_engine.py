from datetime import datetime, time, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import WorkingHours, User
from app.services.google_api import GoogleCalendarService
from zoneinfo import ZoneInfo

class SlotEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.google_service = GoogleCalendarService(db)

    async def get_available_slots(self, user_id: int, target_date: datetime):
        """Получает список свободных слотов для пользователя на указанную дату."""
        # 1. Получаем пользователя и его часовой пояс
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        tz = ZoneInfo(user.timezone if user and user.timezone else "UTC")

        # 2. Получаем рабочий график на этот день недели
        day_of_week = target_date.weekday() # 0 = Понедельник
        result = await self.db.execute(
            select(WorkingHours).where(
                WorkingHours.user_id == user_id,
                WorkingHours.day_of_week == day_of_week
            )
        )
        working_day = result.scalar_one_or_none()
        
        if not working_day:
            return []

        # 3. Формируем границы рабочего дня в часовом поясе организатора
        start_dt = datetime.combine(target_date.date(), working_day.start_time).replace(tzinfo=tz)
        end_dt = datetime.combine(target_date.date(), working_day.end_time).replace(tzinfo=tz)

        # 4. Запрашиваем занятость у Google
        busy_intervals = await self.google_service.get_freebusy(user_id, start_dt, end_dt)

        # 5. Нарезаем рабочий день на 60-минутные слоты
        available_slots = []
        current_slot_start = start_dt

        while current_slot_start + timedelta(hours=1) <= end_dt:
            current_slot_end = current_slot_start + timedelta(hours=1)
            
            # Проверяем, не пересекается ли этот слот с занятыми интервалами Google
            is_busy = False
            for busy in busy_intervals:
                # Парсим время из Google
                busy_start = datetime.fromisoformat(busy["start"].replace("Z", "+00:00")).astimezone(tz)
                busy_end = datetime.fromisoformat(busy["end"].replace("Z", "+00:00")).astimezone(tz)

                # Если слот пересекается с занятым временем — помечаем как занятый
                if not (current_slot_end <= busy_start or current_slot_start >= busy_end):
                    is_busy = True
                    break
            
            if not is_busy:
                # Сохраняем только начало слота в формате строки "HH:MM"
                available_slots.append(current_slot_start.strftime("%H:%M"))
            
            current_slot_start += timedelta(hours=1)

        return available_slots
