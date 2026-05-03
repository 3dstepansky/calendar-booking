from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.db.session import get_db
from app.db.models import User, WorkingHours, Booking
from app.schemas.organizer import WorkingHoursUpdate
from app.api.v1.deps import get_current_user

router = APIRouter()

@router.post("/working-hours")
async def update_working_hours(
    data: WorkingHoursUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить рабочие часы для ТЕКУЩЕГО (авторизованного) организатора.
    Безопасно: ID берется из JWT-токена.
    """
    # 1. Удаляем старые часы именно этого юзера
    await db.execute(delete(WorkingHours).where(WorkingHours.user_id == current_user.id))

    # 2. Добавляем новые
    for day in data.days:
        new_hours = WorkingHours(
            user_id=current_user.id,
            day_of_week=day.day_of_week,
            start_time=day.start_time,
            end_time=day.end_time
        )
        db.add(new_hours)

    await db.commit()
    return {"status": "success", "message": f"Рабочие часы для {current_user.email} обновлены"}

from pydantic import BaseModel
class ProfileUpdate(BaseModel):
    timezone: str

@router.post("/profile")
async def update_profile(
    data: ProfileUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление профиля (часового пояса)"""
    current_user.timezone = data.timezone
    await db.commit()
    return {"status": "success", "message": "Профиль обновлен"}

@router.get("/bookings")
async def get_my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список всех бронирований для организатора"""
    result = await db.execute(
        select(Booking).where(Booking.organizer_id == current_user.id).order_by(Booking.start_time.desc())
    )
    bookings = result.scalars().all()
    return bookings

@router.delete("/bookings/{booking_id}")
async def delete_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отменить бронирование и удалить из Google Calendar"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id, Booking.organizer_id == current_user.id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    # 1. Пытаемся удалить из Google Calendar, если есть event_id
    if booking.google_event_id:
        from app.services.google_api import GoogleCalendarService
        try:
            service = GoogleCalendarService(db)
            await service.delete_event(current_user.id, booking.google_event_id)
        except Exception as e:
            print(f"Failed to delete from Google Calendar: {e}")
            # Мы продолжаем удаление из нашей БД даже если Google API временно недоступен

    # 2. Удаляем из нашей БД
    await db.delete(booking)
    await db.commit()
    
    return {"status": "success", "message": "Бронирование отменено"}
