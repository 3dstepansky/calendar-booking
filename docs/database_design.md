# Проектирование базы данных и архитектурный анализ

В этом документе зафиксированы ключевые решения по структуре данных и логике приложения для записи в Google Calendar.

---

## 1. Анализ архитектуры

### Stateless API (JWT)
Мы используем **JWT** (JSON Web Tokens) для управления сессиями. 
- **Почему:** Фронтенд (React на GitHub Pages) и Бэкенд (FastAPI) находятся на разных доменах. Куки (Sessions) в такой конфигурации сложны в настройке из-за политик CORS и SameSite. JWT передается в заголовке `Authorization`, что делает API мобильным и независимым от домена.

### Метод Freebusy (Privacy-First)
Мы **не храним** копию календаря пользователя. 
- **Почему:** Это упрощает соответствие GDPR/Privacy Policy и избавляет от проблем с рассинхронизацией. При запросе слотов мы «на лету» спрашиваем у Google занятые интервалы и вычитаем их из наших «рабочих часов».

### Race Condition (Блокировки)
Защита от двойного бронирования реализована через **SELECT ... FOR UPDATE**.
- **Почему:** Если два гостя одновременно нажмут «Забронировать» на один слот, база данных выстроит их в очередь. Второй запрос увидит, что слот уже занят первым, и получит ошибку 409 Conflict.

---

## 2. Схема базы данных (SQLAlchemy 2.0 + Async)

Используется современный синтаксис с типами `Mapped` для максимальной поддержки статической типизации.

```python
from datetime import datetime, time
from typing import List, Optional
from sqlalchemy import ForeignKey, String, DateTime, Time, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    """
    Организатор встреч.
    Храним только базовую инфу и ID Google для связи.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    timezone: Mapped[Optional[str]] = mapped_column(String(50), default="UTC")
    google_id: Mapped[str] = mapped_column(String(255), unique=True)
    
    oauth_token: Mapped["OAuthToken"] = relationship(back_populates="user", cascade="all, delete-orphan")
    working_hours: Mapped[List["WorkingHours"]] = relationship(back_populates="user")
    bookings: Mapped[List["Booking"]] = relationship(back_populates="organizer")

class OAuthToken(Base):
    """
    Токены доступа Google. 
    Refresh token критически важен для обновления доступа без участия юзера.
    """
    __tablename__ = "oauth_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    access_token: Mapped[str] = mapped_column(String(512))
    refresh_token: Mapped[Optional[str]] = mapped_column(String(512))
    expires_at: Mapped[datetime] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="oauth_token")

class WorkingHours(Base):
    """
    Настройки доступности (например, Пн-Пт с 09:00 до 18:00).
    """
    __tablename__ = "working_hours"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    day_of_week: Mapped[int] = mapped_column(Integer)  # 0 (Mon) - 6 (Sun)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    user: Mapped["User"] = relationship(back_populates="working_hours")

class Booking(Base):
    """
    Записи на встречу.
    Именно по этой таблице проверяется доступность внутри нашей системы.
    """
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    
    guest_name: Mapped[str] = mapped_column(String(255))
    guest_email: Mapped[str] = mapped_column(String(255))
    
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    
    google_event_id: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organizer: Mapped["User"] = relationship(back_populates="bookings")
```

---

## 3. Обоснование выбора полей

| Поле | Обоснование |
| :--- | :--- |
| `OAuthToken.refresh_token` | Google выдает его один раз (при первом логине). Если мы его не сохраним, мы не сможем зайти в календарь организатора, когда он офлайн. |
| `WorkingHours.day_of_week` | Компактный способ хранения графика. Легко фильтровать в SQL: `WHERE day_of_week = :val`. |
| `Booking.start_time` (Index) | Самый частый запрос будет "дай все брони на эту неделю". Индекс здесь обязателен для производительности. |
| `Booking.google_event_id` | Позволяет синхронизировать изменения. Если гость отменит запись у нас, мы по этому ID удалим событие в Google Calendar. |

---

## 4. Как это работает под капотом (SQLAlchemy 2.0)

1.  **Mapped[int]**: Это аннотации типов для Python. Они не создают колонку сами по себе, но подсказывают SQLAlchemy, какой тип данных ожидать.
2.  **mapped_column**: Это фактическое определение колонки в БД.
3.  **relationship**: Это не колонки в БД, а "умные" свойства Python-объектов, которые позволяют легко прыгать между связанными таблицами (например, от Токена к Юзеру).
