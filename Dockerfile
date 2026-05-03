# Используем официальный легкий образ Python
FROM python:3.11-slim

# Запрещаем Python писать файлы .pyc и включаем небуферизированный вывод (для логов)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /code

# Устанавливаем системные зависимости для работы с Postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Копируем весь код проекта в контейнер
COPY . .

# Команда для запуска сервера (uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
