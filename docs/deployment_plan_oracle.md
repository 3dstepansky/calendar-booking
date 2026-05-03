# Отчет о развертывании: Oracle Cloud Production

Этот документ фиксирует финальную конфигурацию системы после успешного развертывания 3 мая 2026 года.

## 1. Спецификации сервера
- **Host:** `140.238.153.123` (Ubuntu 24.04.4 LTS)
- **Ресурсы:** 24 GB RAM, ARM64 Architecture.
- **Docker Engine:** v29.3.0

## 2. Архитектура развертывания
В ходе работы была выбрана стратегия **локальной сборки на сервере (Local Build)**. Это позволило избежать проблем с правами доступа к приватным образам в GitHub Container Registry и обеспечило максимальную скорость работы.

### Компоненты системы (Docker):
1. **calendar-app (FastAPI):**
   - Порт: `8000` (внешний)
   - Режим: Автоматический перезапуск (`always`)
   - Связь: Настроен на общение с БД через внутреннюю сеть Docker.
2. **calendar-db (PostgreSQL 15):**
   - Порт: `5432` (внутренний)
   - Хранение: Данные сохраняются в Docker Volume `postgres_data`.

## 3. Настройки окружения (.env)
На сервере сконфигурированы следующие боевые параметры:
- `GOOGLE_REDIRECT_URI`: `http://140.238.153.123:8000/api/v1/auth/callback`
- `FRONTEND_URL`: `https://3dstepansky.github.io/calendar-booking/`
- `DATABASE_URL`: `postgresql+asyncpg://postgres:postgres@db:5432/calendar_booking`

## 4. Статус и ссылки
- **Backend API Docs:** [http://140.238.153.123:8000/docs](http://140.238.153.123:8000/docs) — **LIVE**
- **Frontend App:** [https://3dstepansky.github.io/calendar-booking/](https://3dstepansky.github.io/calendar-booking/) — **LIVE**
- **Database Migrations:** Успешно применены до версии `5984a03d2f4b` (add_timezone_to_user).

## 5. Обслуживание (Полезные команды на сервере)
Для управления приложением используйте следующие команды в папке `~/calendar-booking`:
- `sudo docker compose ps` — проверка статуса контейнеров.
- `sudo docker compose logs -f app` — просмотр логов бэкенда в реальном времени.
- `sudo docker compose restart app` — перезапуск приложения после изменений.
