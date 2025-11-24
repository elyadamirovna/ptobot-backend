#!/bin/bash

# Запуск FastAPI через Uvicorn
uvicorn main:app --host 0.0.0.0 --port $PORT

