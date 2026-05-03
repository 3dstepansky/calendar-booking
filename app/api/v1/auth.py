from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import jose.jwt as jwt
import httpx # Мы будем использовать httpx для прямого запроса к Google

from app.core.config import settings
from app.db.session import get_db
from app.db.models import User, OAuthToken

router = APIRouter()

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.freebusy",
]

@router.get("/login")
async def login():
    """Шаг 1: Формируем ссылку вручную, чтобы избежать проблем с состоянием (state)"""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    return RedirectResponse(url)

@router.get("/callback")
async def callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Шаг 2: Обмениваем код на токены напрямую через POST запрос"""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Код авторизации не найден")

    # Прямой запрос к Google для получения токенов
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
    
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Ошибка обмена кода: {token_response.text}")
    
    tokens = token_response.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in")

    # Получаем инфо о пользователе
    async with httpx.AsyncClient() as client:
        user_info_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
    
    user_info = user_info_res.json()
    email = user_info.get("email")
    google_id = user_info.get("id")
    full_name = user_info.get("name")

    # Ищем/Создаем пользователя
    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(email=email, google_id=google_id, full_name=full_name)
        db.add(user)
        await db.flush()

    # Обновляем токены
    result = await db.execute(select(OAuthToken).where(OAuthToken.user_id == user.id))
    token_record = result.scalar_one_or_none()

    if not token_record:
        token_record = OAuthToken(user_id=user.id)
        db.add(token_record)

    token_record.access_token = access_token
    if refresh_token:
        token_record.refresh_token = refresh_token
    
    # Считаем время истечения
    token_record.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    await db.commit()

    # Создаем JWT
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    jwt_token = jwt.encode(token_data, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

    redirect_url = f"{settings.FRONTEND_URL.rstrip('/')}/#/auth/callback?token={jwt_token}"
    return RedirectResponse(redirect_url)
