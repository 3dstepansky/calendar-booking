from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.db.session import get_db
from app.db.models import User, WorkingHours
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
