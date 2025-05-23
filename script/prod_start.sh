#!/bin/bash

set -e

cd "$(dirname "$0")/.."

# Verifica che il file .env esista
if [ ! -f .env ]; then
    echo ".env non trovato, avvio script di setup..."
    ./script/prod_setup.sh
fi

# Verifica che i container necessari siano attivi
if ! docker compose ps | grep -q 'Up'; then
    echo "I container non sono attivi. Avviali prima di proseguire."
    exit 1
fi

uv sync

# Comandi Django
source .venv/bin/activate 2>/dev/null || true

uv run manage.py makemigrations
uv run manage.py migrate
uv run manage.py collectstatic --noinput
uv run manage.py sadmin

echo "Avvio Gunicorn..."
uv run gunicorn --bind 0.0.0.0:8000 core.wsgi:application
