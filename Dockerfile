FROM python:3.12-alpine

# Создание рабочей директории
WORKDIR /app

# Копирование requirements.txt (исправленная версия)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY /src /app

# Открытие порта приложения
EXPOSE 5000

ENTRYPOINT ["flask", "run", "--host", "0.0.0.0"]

