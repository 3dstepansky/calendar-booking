from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.booking import SlotRequest
from app.services.slot_engine import SlotEngine

router = APIRouter()

@router.post("/available")
async def get_available_slots(request: SlotRequest, db: AsyncSession = Depends(get_db)):
    """
    Получение списка свободных слотов для организатора на выбранную дату.
    Теперь работает на реальных данных из Google Calendar!
    """
    engine = SlotEngine(db)
    slots = await engine.get_available_slots(request.organizer_id, request.date)
    
    return {
        "organizer_id": request.organizer_id,
        "date": request.date.date(),
        "slots": slots
    }
