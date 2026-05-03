from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class SlotRequest(BaseModel):
    """Схема данных для запроса доступных слотов"""
    organizer_id: int = Field(..., description="ID организатора, к которому хотим записаться")
    date: datetime = Field(..., description="Дата, на которую ищем свободные окна")

class BookingCreate(BaseModel):
    """Схема для создания нового бронирования"""
    organizer_id: int
    guest_name: str = Field(..., min_length=2, max_length=50)
    guest_email: EmailStr
    start_time: datetime
    end_time: datetime
