from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.booking import BookingCreate
from app.services.booking_service import BookingService
from app.services.telegram_bot import TelegramService
from app.core.config import settings

router = APIRouter()

@router.post("/")
async def create_booking(booking: BookingCreate, db: AsyncSession = Depends(get_db)):
    """
    Создание бронирования. 
    Использует блокировку БД для предотвращения двойной записи.
    """
    service = BookingService(db)
    result = await service.create_booking(booking)
    
    # Отправка уведомления
    tg_service = TelegramService()
    if settings.ADMIN_CHAT_ID:
        msg = (
            f"<b>✅ Новое бронирование!</b>\n"
            f"👤 Гость: {result.guest_name}\n"
            f"📧 Email: {result.guest_email}\n"
            f"⏰ Время: {result.start_time.strftime('%Y-%m-%d %H:%M')}"
        )
        await tg_service.send_booking_notification(settings.ADMIN_CHAT_ID, msg)

    return {
        "status": "success",
        "booking_id": result.id,
        "message": f"Встреча для {result.guest_name} успешно создана"
    }
