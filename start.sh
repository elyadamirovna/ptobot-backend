#!/bin/bash

# Применить миграции Alembic
alembic upgrade head

# Запустить FastAPI через Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port $PORT
