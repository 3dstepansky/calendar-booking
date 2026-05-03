from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Создаем асинхронный движок
# echo=True полезен при разработке — он выводит все SQL-запросы в консоль
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии БД в роутерах.
    Гарантирует закрытие сессии после выполнения запроса.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
