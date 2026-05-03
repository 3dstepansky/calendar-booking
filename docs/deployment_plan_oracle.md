# План развертывания бэкенда: Oracle Server Deployment

Этот план описывает процесс переноса бэкенда из GitHub Container Registry (GHCR) на выделенный сервер Oracle через SSH.

## 1. Фаза аудита и расширения контекста (Безопасная разведка)
Прежде чем начинать деплой, необходимо понять ограничения среды. Я буду использовать следующие команды:

### Аудит сетевых возможностей
- `ss -tulpn` или `netstat -tulpn` — чтобы узнать, какие порты уже заняты (особенно 80, 443, 8000).
- `sudo ufw status` или `sudo iptables -L` — проверка правил брандмауэра (открыт ли доступ извне).

### Аудит ресурсов и окружения
- `docker info` — проверка, установлен ли Docker и достаточно ли прав у текущего пользователя.
- `free -h` — проверка оперативной памяти (важно для работы PostgreSQL).
- `cat /etc/os-release` — определение дистрибутива (Ubuntu/Oracle Linux) для специфичных настроек.

---

## 2. Подготовительная фаза
1. **Авторизация в GHCR:**
   ```bash
   echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
   ```
2. **Настройка окружения:**
   - Создание папки проекта: `mkdir -p ~/calendar-booking`.
   - Создание файла `.env` с боевыми ключами (Google OAuth, Telegram Token).

---

## 3. Фаза развертывания (Execution)
1. **Создание Docker Compose файла:**
   Я создам оптимизированный `docker-compose.prod.yml`, который будет использовать готовый образ из GitHub:
   ```yaml
   services:
     app:
       image: ghcr.io/3dstepansky/calendar-booking-backend:main
       ports:
         - "8000:8000"
       env_file: .env
     db:
       image: postgres:15-alpine
       # ... настройки БД ...
   ```
2. **Запуск:**
   ```bash
   docker-compose up -d
   ```
3. **Миграции:**
   ```bash
   docker-compose exec app alembic upgrade head
   ```

---

## 4. Верификация и Релиз
- **Тест API:** Проверка `https://your-oracle-ip:8000/docs`.
- **Логи:** `docker-compose logs -f app` для отслеживания ошибок в реальном времени.
- **Интеграция:** Обновление ссылки на бэкенд во фронтенде (GitHub Pages).

---

## 5. Безопасность
- [ ] Ограничение доступа к порту 5432 (PostgreSQL) только для локальной сети.
- [ ] Настройка автоматического перезапуска контейнеров (`restart: always`).
- [ ] (Опционально) Настройка Nginx в качестве реверс-прокси для работы по 443 порту, если VPN позволит разделить трафик.
