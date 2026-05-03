from pydantic import BaseModel, Field, field_validator
from datetime import time
from typing import List

class WorkingDay(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0 - Понедельник, 6 - Воскресенье")
    start_time: time
    end_time: time

    @field_validator('end_time')
    @classmethod
    def end_must_be_after_start(cls, v: time, info):
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('Время окончания должно быть позже времени начала')
        return v

class WorkingHoursUpdate(BaseModel):
    days: List[WorkingDay]
