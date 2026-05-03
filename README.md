# Calendar Booking System 📅

Современная система бронирования встреч, интегрированная с Google Calendar и Telegram Mini App.

[![Deploy Frontend to GitHub Pages](https://github.com/3dstepansky/calendar-booking/actions/workflows/deploy.yml/badge.svg)](https://github.com/3dstepansky/calendar-booking/actions/workflows/deploy.yml)

## 🚀 Live Demo
**Фронтенд доступен здесь:** [https://3dstepansky.github.io/calendar-booking/](https://3dstepansky.github.io/calendar-booking/)

## ⚠️ Текущий статус (Backend MVP & Guest UI)
Проект представляет собой работающий прототип (Proof of Concept), в котором полностью реализована сложная логика взаимодействия с API Google и защита от двойных бронирований.

- **✅ Готово (Флоу Гостя):** Гость может зайти на фронтенд, увидеть реальные свободные слоты организатора и совершить бронирование. Бэкенд создает событие в Google Календаре организатора.
- **🚧 В разработке (Флоу Организатора):** В данный момент отсутствует пользовательский интерфейс (UI) для самого организатора. Чтобы организатор мог подключить свой календарь и задать рабочие часы, необходимо создать панель управления (Dashboard). Сейчас эти настройки вносятся напрямую в БД или через прямые API-запросы.

---

## ✨ Основные возможности
- **Интеграция с Google Calendar:** Автоматическая проверка занятости через `freebusy` и создание событий.
- **Умный Slot Engine:** Динамический расчет доступных окон с учетом рабочих часов и часовых поясов.
- **Telegram Mini App:** Интерфейс, оптимизированный для мобильных устройств внутри Telegram.
- **Уведомления:** Мгновенные подтверждения через Telegram Bot API.
- **Безопасность:** Защита от двойного бронирования (Race Condition) и JWT-авторизация.

## 🛠 Технологический стек
- **Backend:** FastAPI (Python 3.11), SQLAlchemy 2.0, PostgreSQL.
- **Frontend:** React + Vite, TypeScript, Framer Motion.
- **DevOps:** Docker, GitHub Actions, Alembic.

## 📦 Быстрый старт

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/3dstepansky/calendar-booking.git
   cd calendar-booking
   ```

2. **Настройте окружение:**
   Создайте файл `.env` на основе примера и заполните ключи Google и Telegram.

3. **Запустите через Docker:**
   ```bash
   docker-compose up -d --build
   ```

4. **Примените миграции:**
   ```bash
   docker-compose exec app alembic upgrade head
   ```

---
*Developed with Antigravity Engine.*
