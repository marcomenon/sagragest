#!/bin/bash
set -e

# Variabili superuser
DJANGO_USER="admin"
DJANGO_PASS="devadmin2137"
DJANGO_FIRST="Super"
DJANGO_LAST="Admin"
DJANGO_EMAIL="admin@example.com"

echo "==> Clonazione repo..."
git clone https://github.com/marcomenon/django-sagragest.git sagragest
cd sagragest

echo "==> Creazione ambiente virtuale..."
python3.12 -m venv .venv
source .venv/bin/activate

echo "==> Installazione pacchetti..."
uv pip install -r requirements.txt

echo "==> Verifica progetto..."
python manage.py check

echo "==> Creazione file di migrazione..."
python manage.py makemigrations accounts printers reports sagragest sagrarapid

echo "==> Applicazione migrazioni..."
python manage.py migrate

echo "==> Raccolta file statici..."
python manage.py collectstatic --noinput

echo "==> Creazione superutente Django..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="$DJANGO_USER").exists():
    User.objects.create_superuser(
        username="$DJANGO_USER",
        password="$DJANGO_PASS",
        email="$DJANGO_EMAIL",
        first_name="$DJANGO_FIRST",
        last_name="$DJANGO_LAST"
    )
EOF

echo "==> Avvio Gunicorn su 0.0.0.0:8000"
gunicorn core.wsgi:application --bind 0.0.0.0:8000
