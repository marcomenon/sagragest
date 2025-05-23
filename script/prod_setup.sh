#!/bin/bash

set -e

echo "Configurazione file .env per SagraGest produzione"

read -p "Inserisci ALLOWED_HOSTS (es: dominio.com,127.0.0.1): " ALLOWED_HOSTS
read -p "Inserisci il dominio pubblico (DOMINIO): " DOMINIO
read -p "Username superuser Django: " DJANGO_SUPERUSER_USERNAME
read -p "Nome superuser Django: " DJANGO_SUPERUSER_NAME
read -p "Cognome superuser Django: " DJANGO_SUPERUSER_LAST_NAME
read -p "Email superuser Django: " DJANGO_SUPERUSER_EMAIL
read -p "Password superuser Django: " DJANGO_SUPERUSER_PASSWORD

# Prepara la stringa ALLOWED_HOSTS includendo sempre localhost, 127.0.0.1 e il dominio
ALLOWED_HOSTS="localhost,127.0.0.1,$DOMINIO,$ALLOWED_HOSTS"

cat > .env <<EOF
# Esempio di file .env per SagraGest
# Personalizza i valori, non committare mai il vero .env!

# 🔐 Sicurezza
DJANGO_SECRET_KEY=$(openssl rand -base64 48 | tr -d '\n' | tr -d '=+/')

# 🗄️ Database PostgreSQL (in container)
POSTGRES_DB=db
POSTGRES_USER=dbuser
POSTGRES_PASSWORD=dbpassword
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

# 🌐 Host consentiti
ALLOWED_HOSTS=$ALLOWED_HOSTS

# 🔁 Redis (in container)
REDIS_URL=redis://127.0.0.1:6379/1

# 🧾 Static & Media
STATIC_ROOT=/staticfiles
MEDIA_ROOT=/media

# ✉️ Email SMTP
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
DJANGO_EMAIL_HOST=smtp.example.com
DJANGO_EMAIL_PORT=587
DJANGO_EMAIL_HOST_USER=your_email@example.com
DJANGO_EMAIL_HOST_PASSWORD=your_email_password
DJANGO_EMAIL_USE_TLS=True

# 🖨️ CUPS server (sull'host)
CUPS_SERVER=localhost
CUPS_HOST=localhost
CUPS_PORT=631
CUPS_ADMIN=admin
CUPS_PASSWORD=admin

# 🐍 Python
DJANGO_ENV=prod
DJANGO_SUPERUSER_USERNAME=$DJANGO_SUPERUSER_USERNAME
DJANGO_SUPERUSER_EMAIL=$DJANGO_SUPERUSER_EMAIL
DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD
DJANGO_SUPERUSER_NAME=$DJANGO_SUPERUSER_NAME
DJANGO_SUPERUSER_LAST_NAME=$DJANGO_SUPERUSER_LAST_NAME

# 🐳 Docker
TZ=Europe/Rome

# 🖧 Samba
SAMBA_USER=smbuser
SAMBA_PASS=smbpass

DOMINIO=$DOMINIO
EOF

echo "File .env creato!"