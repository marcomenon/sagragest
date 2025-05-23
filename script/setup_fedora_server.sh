#!/bin/bash

set -e

echo "Aggiornamento sistema..."
sudo dnf update -y

echo "Installazione dei pacchetti di base..."
sudo dnf install -y \
    python3 python3-pip python3-venv git curl \
    gcc redhat-rpm-config python3-devel \
    libjpeg-turbo-devel zlib-devel \
    cups-devel \
    cairo-devel pango-devel gdk-pixbuf2-devel libffi-devel \
    libxml2-devel libxslt-devel freetype-devel fontconfig \
    openssl-devel pkgconfig

echo "Installazione di uv (gestore ambienti Python)..."
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "Rimozione di eventuali vecchie versioni di Docker..."
sudo dnf remove -y docker \
    docker-client \
    docker-client-latest \
    docker-common \
    docker-latest \
    docker-latest-logrotate \
    docker-logrotate \
    docker-selinux \
    docker-engine-selinux \
    docker-engine

echo "Installazione dei plugin DNF necessari..."
sudo dnf -y install dnf-plugins-core

echo "Aggiunta del repository Docker..."
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

echo "Installazione di Docker e dei plugin aggiuntivi..."
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "Abilitazione e avvio dei servizi Docker e containerd..."
sudo systemctl enable --now docker.service
sudo systemctl enable --now containerd.service

echo "Creazione del gruppo docker (se non esiste)..."
sudo groupadd -f docker

echo "Aggiunta dell'utente corrente al gruppo docker..."
sudo usermod -aG docker $USER

echo "Aggiornamento del gruppo corrente (newgrp docker)..."
newgrp docker <<EONG
echo "Gruppo docker attivo nella shell corrente."
EONG

echo "Installazione completata!"
echo "ATTENZIONE: per usare Docker senza sudo in tutte le shell, esegui 'logout' e rientra."