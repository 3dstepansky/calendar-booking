from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import jose.jwt as jwt
from jose import JWTError

from app.core.config import settings
from app.db.session import get_db
from app.db.models import User

# Инструмент для извлечения токена из заголовка Authorization
security = HTTPBearer()

async def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Проверка JWT-токена и получение текущего пользователя из БД.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить личность. Пожалуйста, войдите снова.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Расшифровываем токен нашим секретным ключом
        payload = jwt.decode(
            auth.credentials, 
            settings.JWT_SECRET, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Ищем пользователя в базе данных
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return user
