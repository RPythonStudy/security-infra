==============================================================================
security-infra: 미래형 의료 데이터 보안/인증/감사 인프라 자동화
==============================================================================

## 개요

**security-infra**는 pseudonymee 프로젝트의  
_인증, 비밀관리, 감사, 로그, 계정관리_ 등 모든 보안/운영 인프라를  
Docker 컨테이너 기반으로 일관되게 자동화하는 플랫폼입니다.

**주요 포함 서비스:**
- **HashiCorp Vault** (비밀/키/정책 관리, File Seal 지원)
- **ELK Stack** (Elasticsearch, Logstash, Kibana: 이중 로그 및 감사)
- **Keycloak** (ID/Token 인증)
- **OpenLDAP** (계정 관리)

> 모든 운영은 **CLI 자동화**, **sudo 기반 docker compose**로 관리  
> (실시간 감사 추적과 인프라 복구/확장까지 고려)

## 폴더 구조 요약

- `security-infra/`
    - `config/`           : 서비스별 설정파일 (YAML, HCL 등)
    - `docker/`           : 서비스별 볼륨/설정/인증서 경로 (버전관리 제외)
    - `logger/`           : Python 로깅 유틸
    - `logs/`             : 인프라/감사 로그
    - `src/security_infra/` : 자동화 스크립트 (config_loader, create_directories 등)
    - `templates/`        : ELK/Vault 등 템플릿 config 원본
    - `tests/`            : 자동화 코드 테스트
    - `docker-compose.yml`: 인프라 통합 docker compose
    - `security-infra-cli.py`: CLI 자동화 진입점 (typer 기반)
    - `README.md`         : 설명서

## 주요 기능 및 자동화 명령어

### 환경 준비
- WINDOWS 10/11에서 WSL2
- DOCKER 설치
- Python
- Docker Compose
- Git

### Clone 및 초기화
- git clone
- .venv 가상환경 생성
-  pip upgrade
-  pip intsall -e .
-  pip install -r requirements.txt

### CLI 명령어
- `security-infra-cli.py`를 통해 CLI 명령어 실행

#### 필수폴더 자동 생성
```bash
python security-infra-cli.py create-directories
```
- 권한 문제시 --force 사용, 권한 에러는 sudo로 자동 재시도

#### 서비스 인증서/키 자동 생성
```bash
python security-infra-cli.py generate-certificates
```
- vault, elk, keycloak 등 SAN 자동구성, 덮어쓰기는 --overwrite 옵션 사용

#### 템플릿 config 복사
```bash
python security-infra-cli.py sync-templates
```
- ELK, Vault 등 템플릿 config를 config/ 폴더로 복# templates/ → docker/ 각 서비스 경로로 자동 복사

#### sudoers 설정 방법
- 자동화/무인화를 위해 아래와 같이 sudoers 파일에 docker 명령 패스워드 없이 허용을 추가해야 합니다.

```bash
whoami
```
- 예시: ben

- sudoers 편집 (visudo 권장)
```bash
sudo visudo /etc/sudoers.d.docker
```
- 아래 내용을 추가하여 docker, docker-compose 명령어를 sudo 없이 실행 가능하게 설정합니다.
```bash
<USERNAME> ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/bin/docker-compose
```

- 검증
```bash
sudo -n docker ps
```

#### Bitwarden server 도커 컨테이너 설치
https://github.com/bitwarden/server#building
- DNS 설정은 패스
- Docker와 Docker Compose가 설치는 이미 되어 있어야 합니다.
- Bitwarden 서버를 설치하기 위해 아래 명령어를 실행합니다.


#### Docker 서비스 컨트롤
```bash
python security-infra-cli.py compose up --service all
python security-infra-cli.py compose down --service vault
python security-infra-cli.py compose restart --service elk
```
- `--service` 옵션으로 특정 서비스 컨트롤 가능# 모든 명령은 sudo docker compose 기반 (sudoers 설정 권장)

#### Vault 초기화 및 unseal 키 안전보관
- 보안을 위해 이 단계는 터미널에서 수동으로 진행됩니다.
```bash
sudo docker exec -it vault vault operator init -key-shares=5 -key-threshold=3
```
Unseal Key 1 ~5 까지를 Bitwarden에 안전하게 보관

#### 개인정보보호를 위한 역할분담 예시

1. Vault Unseal Key Keeper 역할 분장 설계

| Vault 내 역할명     | 계정ID         | 이메일                                                           | 역할설명                | Unseal Key 보관 | 비고 |
| --------------- | ------------ | ------------------------------------------------------------- | ------------------- | ------------- | -- |
| 볼트 최고관리자        | vault-root   | [vault-root@rpython.stdy](mailto:vault-root@rpython.stdy)     | Vault Root 권한       | 1번            |    |
| 볼트 운영자          | vault-ops    | [vault-ops@rpython.stdy](mailto:vault-ops@rpython.stdy)       | Vault 차기운영/복구 권한    | 2번            |    |
| 가명화정보담당자        | pseudo-info  | [pseudo-info@rpython.stdy](mailto:pseudo-info@rpython.stdy)   | 가명화 정보 총괄           | 3번            |    |
| pseudonymee 책임자 | pseudo-chief | [pseudo-chief@rpython.stdy](mailto:pseudo-chief@rpython.stdy) | pseudonymee 프로젝트 책임 | 4번            |    |
| pseudonymee 운영자 | pseudo-ops   | [pseudo-ops@rpython.stdy](mailto:pseudo-ops@rpython.stdy)     | pseudonymee 운영/일상관리 | 5번            |    |

2. Bitwarden/LDAP/서버 최고관리자 역할 분리 설계

| 시스템구분           | 계정ID        | 이메일                                                         | 역할설명                 | 비고    |
| --------------- | ----------- | ----------------------------------------------------------- | -------------------- | ----- |
| Bitwarden 최고관리자 | bw-admin    | [bw-admin@rpython.stdy](mailto:bw-admin@rpython.stdy)       | Bitwarden Root/Owner | 별도 보관 |
| LDAP 최고관리자      | ldap-admin  | [ldap-admin@rpython.stdy](mailto:ldap-admin@rpython.stdy)   | OpenLDAP 최고권한        | 별도 보관 |
| 서버(공통) 관리자      | infra-admin | [infra-admin@rpython.stdy](mailto:infra-admin@rpython.stdy) | 서버/OS/컨테이너 등 총괄      | 별도 보관 |
