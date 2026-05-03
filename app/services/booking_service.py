from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.db.models import User, Booking
from app.services.google_api import GoogleCalendarService
from app.schemas.booking import BookingCreate

class BookingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.google_service = GoogleCalendarService(db)

    async def create_booking(self, data: BookingCreate):
        """
        Создание бронирования с защитой от Race Condition.
        """
        # 1. Начинаем транзакцию и блокируем запись организатора (SELECT ... FOR UPDATE)
        # Это гарантирует, что в этот момент никто другой не сможет создать бронь для этого юзера
        result = await self.db.execute(
            select(User).where(User.id == data.organizer_id).with_for_update()
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="Организатор не найден")

        # 2. Проверяем, не занят ли уже этот слот в нашей локальной базе
        # (На случай, если кто-то только что успел забронировать)
        existing_booking = await self.db.execute(
            select(Booking).where(
                Booking.organizer_id == data.organizer_id,
                Booking.start_time == data.start_time
            )
        )
        if existing_booking.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Извините, этот слот уже забронирован")

        # 3. (Опционально) Можно еще раз проверить Google Calendar через Freebusy для 100% уверенности
        # Но для простоты примера ограничимся проверкой локальной БД

        # 4. Создаем запись в нашей базе данных
        end_time = data.start_time + timedelta(hours=1) # Предполагаем 1-часовые встречи
        new_booking = Booking(
            organizer_id=data.organizer_id,
            guest_name=data.guest_name,
            guest_email=data.guest_email,
            start_time=data.start_time,
            end_time=end_time
        )
        self.db.add(new_booking)
        
        # 5. Создаем событие в Google Calendar
        try:
            await self.google_service.create_event(
                user_id=data.organizer_id,
                summary=f"Встреча: {data.guest_name}",
                start_time=data.start_time,
                end_time=end_time,
                guest_email=data.guest_email
            )
        except Exception as e:
            # Если Google API упал — откатываем транзакцию, чтобы данные в базе не разошлись
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка Google Calendar: {str(e)}")

        # 6. Фиксируем изменения
        await self.db.commit()
        return new_booking
