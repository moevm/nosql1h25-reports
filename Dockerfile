FROM python:3.12-alpine

WORKDIR /src

# Установка зависимостей
COPY requirements.txt /src
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY /src /src

EXPOSE 5000

ENTRYPOINT ["flask"]
CMD ["run", "--host", "0.0.0.0", "--no-debug", "--port", "5000"]
