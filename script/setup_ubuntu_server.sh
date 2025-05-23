#!/bin/bash
set -e

echo "==> Aggiornamento pacchetti di sistema..."
sudo apt update && sudo apt upgrade -y

echo "==> Installazione dipendenze per Python, CUPS e build..."
sudo apt install -y \
  python3 python3-pip python3-venv python3-dev \
  build-essential pkg-config \
  libffi-dev libssl-dev \
  libcups2 libcups2-dev \
  libjpeg-dev zlib1g-dev libwebp-dev libopenjp2-7-dev \
  libxml2-dev libxslt1-dev \
  libpango1.0-dev libgdk-pixbuf2.0-dev \
  libharfbuzz-dev libfribidi-dev \
  git curl cups ca-certificates

echo "==> Abilitazione servizio CUPS..."
sudo systemctl enable cups
sudo systemctl start cups
sudo usermod -aG lpadmin $USER

echo "==> Installazione UV (Python package manager)..."
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "==> Rimozione pacchetti Docker preesistenti (se presenti)..."
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt-get remove -y $pkg || true
done

echo "==> Installazione chiave GPG di Docker..."
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc > /dev/null
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "==> Aggiunta repository Docker..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update

echo "==> Installazione Docker..."
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "==> Abilitazione Docker al boot..."
sudo systemctl enable docker.service
sudo systemctl enable containerd.service

echo "==> Aggiunta utente al gruppo docker..."
sudo groupadd docker || true
sudo usermod -aG docker $USER

echo "==> Applicazione nuovo gruppo docker (valido solo per shell corrente)..."
newgrp docker

echo "✅ Setup completato! Riavvia o esci/rientra nella sessione per usare Docker senza sudo."
