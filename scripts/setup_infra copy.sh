#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# File: setup_infra.sh
# Description: 인프라(ELK, Keycloak, Vault, OpenLDAP 등) 볼륨/디렉토리/권한/인증서 초기화 자동화 스크립트
# Usage: sudo ./scripts/setup_infra.sh
# Author: BenKorea <benkorea.ai@gmail.com>
# Created: 2025-07-03
# ------------------------------------------------------------------------------

set -euo pipefail

# 변수화 (추후 유지보수 편의)
ELK_UID=1000
ELK_GID=1000
KEYCLOAK_UID=1000
KEYCLOAK_GID=0
VAULT_UID=100
VAULT_GID=100
LDAP_UID=101
LDAP_GID=103

echo "### [0/4] 기존 docker 서비스 정지 및 docker 디렉토리 삭제"
sudo docker compose down || true
sudo rm -rf ~/projects/p31211-r450-pseudo_struct/docker

echo "### [1/4] 폴더 생성"
sudo mkdir -p ./docker/elk/esdata ./docker/elk/logstash/pipeline
sudo mkdir -p ./docker/keycloak/data
sudo mkdir -p ./docker/vault/config ./docker/vault/file ./docker/vault/certs ./docker/vault/logs
sudo mkdir -p ./docker/openldap/data ./docker/openldap/config

echo "### [1.5/4] logstash.conf 복사 및 권한 변경"
sudo cp ./config/logstash.conf ./docker/elk/logstash/pipeline/logstash.conf
sudo chown -R ${ELK_UID}:${ELK_GID} ./docker/elk/logstash/pipeline/logstash.conf
sudo chmod -R 750 ./docker/elk/logstash/pipeline/logstash.conf

echo "### [2/4] 권한 및 소유권 변경"
# ELK
sudo chown -R ${ELK_UID}:${ELK_GID} ./docker/elk
sudo chmod -R 750 ./docker/elk

# Keycloak
sudo chown -R ${KEYCLOAK_UID}:${KEYCLOAK_GID} ./docker/keycloak
sudo chmod -R 750 ./docker/keycloak

# Vault
sudo chown -R ${VAULT_UID}:${VAULT_GID} ./docker/vault
sudo chmod -R 750 ./docker/vault

# OpenLDAP
sudo chown -R ${LDAP_UID}:${LDAP_GID} ./docker/openldap
sudo chmod -R 750 ./docker/openldap

echo "### [3/4] Vault 인증서 1회성 생성"
CERT_DIR=./docker/vault/certs
CERT_KEY=${CERT_DIR}/vault.key
CERT_CRT=${CERT_DIR}/vault.crt

if [ ! -f "$CERT_KEY" ] || [ ! -f "$CERT_CRT" ]; then
  sudo openssl req \
    -x509 -newkey rsa:2048 \
    -keyout "$CERT_KEY" \
    -out "$CERT_CRT" \
    -days 14 \
    -nodes \
    -subj "/C=KR/ST=Seoul/L=Seoul/O=KIRAMS/OU=RPythonStudy/CN=localhost" \
    -addext "subjectAltName = DNS:localhost, IP:127.0.0.1, DNS:elasticsearch, DNS:kibana, DNS:logstash, DNS:keycloak, DNS:vault, DNS:openldap"
  sudo chown ${VAULT_UID}:${VAULT_GID} "$CERT_KEY" "$CERT_CRT"
  sudo chmod 640 "$CERT_KEY" "$CERT_CRT"
  echo "Vault 인증서 생성 완료"
else
  echo "Vault 인증서가 이미 존재합니다. (생략)"
fi

echo "### [4/4] 권한 및 파일 검증"
sudo ls -ld ./docker/elk ./docker/elk/esdata ./docker/elk/logstash ./docker/elk/logstash/pipeline
sudo ls -ld ./docker/keycloak ./docker/keycloak/data
sudo ls -ld ./docker/vault ./docker/vault/config ./docker/vault/file ./docker/vault/certs ./docker/vault/logs
sudo ls -l ./docker/vault/certs
sudo openssl x509 -in ./docker/vault/certs/vault.crt -noout -text | grep -E 'Subject:|DNS:|IP Address'
sudo ls -ld ./docker/openldap ./docker/openldap/data ./docker/openldap/config

echo "초기화/권한/인증서 작업 완료"
