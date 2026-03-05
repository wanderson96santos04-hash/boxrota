#!/usr/bin/env bash

set -e

echo "📦 Rodando migrations..."
alembic upgrade head

echo "🚀 Iniciando API BoxRota..."

PORT=${PORT:-8000}

uvicorn app.main:app \
  --host 0.0.0.0 \
  --port $PORT \
  --workers 2