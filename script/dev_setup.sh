#!/bin/bash
set -e

cd "$(dirname "$0")/.."

# Sincronizza dipendenze
uv sync
# Ambiente virtuale
source .venv/bin/activate

# Check e migrazioni
uv run manage.py check
uv run manage.py makemigrations
uv run manage.py migrate
uv run manage.py collectstatic --noinput
uv run manage.py sadmin

echo "==> Avvio DevServer su 0.0.0.0:8000"
uv run manage.py runserver 0.0.0.0:8000