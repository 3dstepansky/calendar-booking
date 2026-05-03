# Calendar Booking API (FastAPI + Google Calendar)

Бэкенд-сервис для автоматизации записи на встречи с интеграцией в Google Calendar. Идеально подходит для Telegram Mini Apps.

## ✨ Основные возможности
- **Google OAuth 2.0:** Безопасная авторизация организаторов.
- **Интеллектуальный SlotEngine:** Расчет свободных окон с учетом реальной занятости в Google Календаре.
- **Защита от Double Booking:** Использование пессимистических блокировок в БД для предотвращения одновременной записи.
- **Полная асинхронность:** FastAPI + SQLAlchemy 2.0 (asyncpg).
- **Docker-ready:** Готовые конфиги для развертывания.

## 🚀 Быстрый старт

1. Скопируйте `.env.example` в `.env` и заполните ключи Google API.
2. Запустите контейнеры:
   ```bash
   docker-compose up -d --build
   ```
3. Примените миграции:
   ```bash
   docker-compose exec app alembic upgrade head
   ```
4. Откройте Swagger UI: `http://localhost:8000/docs`

## 📂 Документация
Подробные руководства находятся в папке `docs/`:
- [Архитектура и БД](docs/database_design.md)
- [План реализации](docs/implementation_plan.md)
- [Руководство пользователя (Walkthrough)](docs/walkthrough.md)

## 🛠 Технологии
- **Python 3.11**
- **FastAPI**
- **PostgreSQL 15**
- **SQLAlchemy 2.0**
- **Alembic**
- **Docker & Docker Compose**
