FROM python:3.12-alpine

WORKDIR /app

# Установка зависимостей
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY /src /app

EXPOSE 5000

ENTRYPOINT ["flask"]
CMD ["run", "--host", "0.0.0.0"]
