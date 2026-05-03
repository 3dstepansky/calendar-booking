from datetime import datetime, time
from typing import List, Optional
from sqlalchemy import ForeignKey, String, DateTime, Time, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    google_id: Mapped[str] = mapped_column(String(255), unique=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    
    oauth_token: Mapped["OAuthToken"] = relationship(back_populates="user", cascade="all, delete-orphan")
    working_hours: Mapped[List["WorkingHours"]] = relationship(back_populates="user")
    bookings: Mapped[List["Booking"]] = relationship(back_populates="organizer")

class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    access_token: Mapped[str] = mapped_column(String(512))
    refresh_token: Mapped[Optional[str]] = mapped_column(String(512))
    expires_at: Mapped[datetime] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="oauth_token")

class WorkingHours(Base):
    __tablename__ = "working_hours"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    day_of_week: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    user: Mapped["User"] = relationship(back_populates="working_hours")

class Booking(Base):
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
