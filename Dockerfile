# Базовый образ с Python 3.9
FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование requirements.txt (исправленная версия)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование остальных файлов
#COPY . .
#COPY /src .
COPY /src /app

# Создание директории для загрузок
RUN mkdir -p /src/app/uploads

# Настройка переменных окружения
#ENV FLASK_APP=src/app.py
ENV FLASK_ENV=production
ENV NEO4J_URI=bolt://db:7687
ENV NEO4J_USER=neo4j
ENV NEO4J_PASSWORD=password

# Открытие порта приложения
EXPOSE 5000

# Команда запуска (production)
#CMD ["flask", "--bind", "0.0.0.0:5001", "--workers", "4", "app:app"]
#CMD ["flask", "run"]

ENTRYPOINT ["flask", "run", "--host", "0.0.0.0"]

