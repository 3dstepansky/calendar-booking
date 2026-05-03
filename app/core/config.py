from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Настройки БД
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/calendar_db"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback"
    
    # JWT
    JWT_SECRET: str = "super-secret-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 дней
    
    # Frontend URL (для редиректа после OAuth)
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Разрешить HTTP для OAuth (только для разработки)
    OAUTHLIB_INSECURE_TRANSPORT: str = "0"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    ADMIN_CHAT_ID: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
