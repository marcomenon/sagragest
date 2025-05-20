FROM python:3.13.3-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Europe/Rome

WORKDIR /app

# Installa dipendenze di sistema per pacchetti Python come weasyprint, pycups, ecc.
RUN apt-get update && apt-get install -y \
    libcups2-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libmagic1 \
    libglib2.0-dev \
    shared-mime-info \
    curl \
    ca-certificates \
    # Aggiungi le dipendenze di WeasyPrint
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    fonts-liberation \
    fonts-dejavu \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    tzdata \
    && ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia uv e installa
COPY --from=ghcr.io/astral-sh/uv:0.7.4 /uv /uvx /bin/

# Copia requirements e installa pacchetti
COPY requirements.txt .
RUN uv pip install -r requirements.txt --system

# Copia il progetto
COPY . .

# Assicura che il socket venga creato in /run
RUN mkdir -p /run && chmod 777 /run

# Copia entrypoint
COPY entrypoint.prod.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Esegui lo script
ENTRYPOINT ["/entrypoint.sh"]