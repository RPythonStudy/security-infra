#!/bin/bash

set -e

sudo mkdir -p \
  /opt/ai4rm/vault/docker/config \
  /opt/ai4rm/vault/docker/file \
  /opt/ai4rm/vault/docker/certs \
  /opt/ai4rm/vault/docker/logs \
  /opt/ai4rm/vault/docker/agent/config \
  /opt/ai4rm/vault/docker/agent/sink

sudo chown -R 100:100 \
  /opt/ai4rm/vault/docker/config \
  /opt/ai4rm/vault/docker/file \
  /opt/ai4rm/vault/docker/certs \
  /opt/ai4rm/vault/docker/logs \
  /opt/ai4rm/vault/docker/agent/config \
  /opt/ai4rm/vault/docker/agent/sink


sudo chmod -R 750 \
  /opt/ai4rm/vault/docker/config \
  /opt/ai4rm/vault/docker/file \
  /opt/ai4rm/vault/docker/certs \
  /opt/ai4rm/vault/docker/logs \
  /opt/ai4rm/vault/docker/agent/config \
  /opt/ai4rm/vault/docker/agent/sink

sudo openssl req \
  -x509 -newkey rsa:2048 \
  -keyout /opt/ai4rm/vault/docker/certs/vault.key \
  -out /opt/ai4rm/vault/docker/certs/vault.crt \
  -days 14 \
  -nodes \
  -subj "/CN=localhost" \
  -addext "subjectAltName = DNS:localhost, IP:127.0.0.1, DNS:elasticsearch, DNS:kibana, DNS:logstash, DNS:keycloak, DNS:vault, DNS:openldap" \
  >/dev/null 2>&1

sudo chown 100:100 /opt/ai4rm/vault/docker/certs/vault.key /opt/ai4rm/vault/docker/certs/vault.crt
sudo chmod 640 /opt/ai4rm/vault/docker/certs/vault.key /opt/ai4rm/vault/docker/certs/vault.crt

sudo cp ./templates/vault/docker-compose.yml  /opt/ai4rm/vault/
sudo cp ./templates/vault/vault.hcl  /opt/ai4rm/vault/docker/config/
sudo cp ./templates/vault/config.hcl /opt/ai4rm/vault/docker/agent/config/

sudo chown 100:100 /opt/ai4rm/vault/docker/config/vault.hcl
sudo chmod 640 /opt/ai4rm/vault/docker/config/vault.hcl
sudo chown 100:100 /opt/ai4rm/vault/docker/agent/config/config.hcl
sudo chmod 640 /opt/ai4rm/vault/docker/agent/config/config.hcl
