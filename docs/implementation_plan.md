# План реализации (Implementation Plan): Calendar Booking API

## Цель проекта
Создать надежный бэкенд для записи к специалисту через Telegram Mini App с двусторонней синхронизацией через Google Calendar API.

---

## 1. Текущий прогресс (Status Quo)

### ✅ Инфраструктура и БД
- [x] Настройка Docker-окружения (FastAPI + PostgreSQL).
- [x] Проектирование схемы БД (Users, OAuthTokens, WorkingHours, Bookings).
- [x] Настройка Alembic для асинхронных миграций.
- [x] Поддержка часовых поясов (Timezone support).

### ✅ Авторизация и Безопасность
- [x] Реализация Google OAuth 2.0 (Flow).
- [x] Хранение и автоматическое обновление `refresh_token`.
- [x] JWT-авторизация для сессий приложения.
- [x] Обработка OAuth Callback на фронтенде.

### ✅ Бизнес-логика и Бэкенд
- [x] Модуль настройки рабочих часов организатора.
- [x] **SlotEngine:** Динамический расчет слотов с учетом часовых поясов.
- [x] **Google Integration:** Запросы `freebusy`.
- [x] Защита от Double Booking через `SELECT FOR UPDATE`.
- [x] **Middleware для логирования:** Мониторинг запросов в реальном времени.
- [x] **Уведомления:** Интеграция с Telegram Bot API.

### ✅ Фронтенд (React + Vite)
- [x] Инициализация проекта и настройка Vite.
- [x] **UI Kit:** Премиальный минималистичный дизайн (Quiet Luxury).
- [x] **Интеграция API:** Связка фронтенда с FastAPI через Axios.
- [x] **Telegram Web App SDK:** Поддержка работы внутри Telegram.

---

## 2. Осталось сделать (Backlog)

### 🛠 Финализация и Деплой
- [ ] **Настройка .env:** Заполнение боевых ключей Google и Telegram.
- [ ] **SSL (HTTPS):** Настройка сертификатов для работы OAuth в продакшене.
- [ ] **Production Docker Compose:** Оптимизация образов для деплоя.

---

## 3. Оценка рисков
- **Rate Limits:** Google API имеет лимиты. Рекомендуется кэширование.
- **Race Conditions:** Решено на уровне БД.
