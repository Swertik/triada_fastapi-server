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

RUN --mount=type=secret,id=group_token,target=/app/triada/config/secrets/group_token \
    cat /app/triada/config/secrets/group_token > /dev/null

RUN --mount=type=secret,id=my_token,target=/app/triada/config/secrets/my_token \
    cat /app/triada/config/secrets/my_token > /dev/null

RUN --mount=type=secret,id=database_url,target=/app/triada/config/secrets/database_url \
    cat /app/triada/config/secrets/database_url > /dev/null


ENV GROUP_TOKEN=/app/triada/config/secrets/group_token
ENV MY_TOKEN=/app/triada/config/secrets/my_token
ENV DATABASE_URL=/app/triada/config/secrets/database_url
ENV REDIS_HOST='redis'
# Переключение на непривилегированного пользователя
USER appuser

# Копирование кода и настройка переменных окружения
# Экспорт порта и запуск приложения
EXPOSE 8080
CMD uvicorn triada.main:app --host 0.0.0.0 --port 8080