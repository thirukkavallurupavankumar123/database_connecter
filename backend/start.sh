#!/bin/bash
# ARGO Backend startup script — runs migrations then starts the server
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting ARGO backend..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
