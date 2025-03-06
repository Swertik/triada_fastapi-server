# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.9
FROM python:${PYTHON_VERSION}-slim as base

# 1. Установка системных зависимостей ДО переключения пользователя
RUN apt-get update && \
    apt-get install -y redis-tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Остальные настройки окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Создание непривилегированного пользователя
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN mkdir -p /app/triada/config/secrets

COPY . .

# Установка Python-зависимостей
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Установка секретов
RUN --mount=type=secret,id=group_token,src=run/secrets/group_token \
    --mount=type=secret,id=my_token,src=run/secrets/my_token \
    --mount=type=secret,id=database_url,src=run/secrets/database_url \
    --mount=type=secret,id=redis_host,src=run/secrets/redis_host


ENV GROUP_TOKEN_FILE=/run/secrets/group_token
ENV MY_TOKEN_FILE=/run/secrets/my_token
ENV DATABASE_URL_FILE=/run/secrets/database_url
ENV REDIS_HOST_FILE=/run/secrets/redis_host

# Переключение на непривилегированного пользователя
USER appuser

# Копирование кода и настройка переменных окружения
# Экспорт порта и запуск приложения
EXPOSE 8080
CMD uvicorn triada.main:app --host 0.0.0.0 --port 8080