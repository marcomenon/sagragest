# SagraGest - Setup e Avvio

## Prerequisiti
- Python >= 3.13
- Docker e Docker Compose
- uv (Python package manager)
- Git

## Setup Fedora
```bash
cd script
chmod +x setup_fedora_server.sh
./setup_fedora_server.sh
```

## Setup Ubuntu
```bash
cd script
chmod +x setup_ubuntu_server.sh
./setup_ubuntu_server.sh
```

## Setup ambiente di sviluppo
```bash
cd script
chmod +x dev_setup.sh
./dev_setup.sh
```

## Setup ambiente di produzione
```bash
cd script
chmod +x prod_setup.sh
./prod_setup.sh
```

## Avvio produzione
```bash
cd script
chmod +x prod_start.sh
./prod_start.sh
```

## Avvio servizi con Docker Compose
```bash
docker compose up -d
```

## File e script principali
- `script/setup_fedora_server.sh` — setup server Fedora
- `script/setup_ubuntu_server.sh` — setup server Ubuntu
- `script/dev_setup.sh` — setup ambiente sviluppo
- `script/prod_setup.sh` — genera il file .env per la produzione
- `script/prod_start.sh` — avvia il progetto in produzione
- `docker-compose.yml` — servizi Postgres, Redis, Nginx
- `nginx/nginx.conf` — configurazione Nginx

## Note
- Il file `.env` viene generato da `prod_setup.sh` e usato sia da Django che da Docker Compose.
- Per usare Docker senza sudo, esegui logout/login dopo il setup.
- Tutti i comandi Django e Gunicorn in sviluppo e produzione usano `uv run`.
- I file statici e media sono serviti da Nginx tramite i volumi `/staticfiles` e `/media`.
