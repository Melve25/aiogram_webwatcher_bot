#!/bin/bash

# Остановить выполнение при ошибке
set -e

# Выполнить миграции
echo "Running Alembic migrations..."
uv run alembic upgrade head

# Запустить бота 
echo "Starting bot..."
uv run python -m app.bot
