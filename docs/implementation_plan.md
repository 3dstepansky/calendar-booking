# План реализации (Implementation Plan): Calendar Booking API

## Цель проекта
Создать надежный бэкенд для записи к специалисту через Telegram Mini App с двусторонней синхронизацией через Google Calendar API.

---

## 1. Текущий статус (Финальная сборка)

### ✅ Инфраструктура и БД
- [x] Настройка Docker-окружения (FastAPI + PostgreSQL).
- [x] Проектирование схемы БД (Users, OAuthTokens, WorkingHours, Bookings).
- [x] Настройка Alembic для асинхронных миграций.
- [x] **Timezone Support:** Поддержка часовых поясов организатора (ZoneInfo).

### ✅ Авторизация и Безопасность
- [x] Реализация Google OAuth 2.0 (Flow).
- [x] Хранение и автоматическое обновление `refresh_token`.
- [x] JWT-авторизация для сессий приложения.
- [x] **GitHub Secret Scanning:** Репозиторий очищен от чувствительных данных.

### ✅ Бизнес-логика и Бэкенд
- [x] Модуль настройки рабочих часов организатора.
- [x] **SlotEngine:** Динамический расчет слотов с учетом TZ.
- [x] **Google Integration:** Запросы `freebusy` и создание событий.
- [x] **Middleware для логирования:** Мониторинг запросов и времени ответа.
- [x] **Уведомления:** Интеграция с Telegram Bot API для подтверждения записей.

### ✅ Фронтенд и Деплой (GitHub Pages)
- [x] **UI Kit:** Минималистичный дизайн в стиле "Quiet Luxury".
- [x] **Интеграция API:** Потребление данных через Axios.
- [x] **Routing:** Настройка React Router с поддержкой `basename`.
- [x] **CI/CD:** GitHub Actions для автоматического деплоя при каждом пуше.
- [x] **Live URL (Front):** [https://3dstepansky.github.io/calendar-booking/](https://3dstepansky.github.io/calendar-booking/)
- [x] **Backend Deployment:** Развернут на сервере Oracle (`140.238.153.123:8000`).
- [x] **Database Migrations:** Успешно применены в продакшн-среде.

---

## 2. Дальнейшие рекомендации
- **Production SSL:** Для работы Google OAuth в облаке требуется HTTPS (решено через GH Pages для фронта, нужно решить для бэкенда).
- **Rate Limiting:** Добавить ограничение запросов (Throttling) для защиты от спама бронирований.
- **Telegram Bot:** Расширение функционала бота для управления записями прямо в чате.
