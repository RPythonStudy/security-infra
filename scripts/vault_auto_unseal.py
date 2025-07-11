# scripts/vault_auto_unseal.py
"""
Vault 자동 언실 스크립트 (재가동/언실 상황만 처리)
- Vault가 sealed 상태일 때만 auto unseal을 진행
- Bitwarden에서 언실키를 안전하게 추출하여 Vault에 자동 제출
"""

import os
import sys
import subprocess
import requests
import json
import urllib3
from security_infra.usb_utils import find_usb_mount_by_label

# ===== 환경설정 =====
VAULT_ADDR = "https://127.0.0.1:8200"     # ★★ 실제 Vault API 주소로 맞출 것
BW_LABEL = "BW_PW_USB"                    # ★★ USB 라벨 실제 환경과 일치시킬 것
BW_FILE = "bt_pw_user1.enc"               # ★★ USB 내 비밀번호 파일명 실제와 일치시킬 것
BW_ITEM = "vault unseal key - desktop"    # ★★ Bitwarden 내 언실키 항목명 실제와 일치시킬 것

os.environ["VAULT_SKIP_VERIFY"] = "true"  # 셀프사인 인증서 무시(개발/테스트 환경)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===== 1. Vault sealed 상태 확인 =====
try:
    r = requests.get(f"{VAULT_ADDR}/v1/sys/seal-status", verify=False)
    if not r.ok:
        print("[ERROR] Vault API 연결 실패:", r.text)
        sys.exit(1)
    status = r.json()
except Exception as e:
    print(f"[ERROR] Vault 상태 조회 실패: {e}")
    sys.exit(1)

if not status.get("sealed", True):
    print("[INFO] Vault는 이미 unsealed 상태입니다. 추가 작업 없이 종료합니다.")
    sys.exit(0)

print("[INFO] Vault is sealed. Auto unseal을 진행합니다.")

# ===== 2. USB에서 Bitwarden 마스터 패스워드 파일 감지 및 읽기 =====
usb_mount = find_usb_mount_by_label(BW_LABEL, test_file=BW_FILE)
if not usb_mount:
    print("[ERROR] USB not detected")
    sys.exit(1)

pw_file = os.path.join(usb_mount, BW_FILE)
with open(pw_file, "r") as f:
    bw_password = f.read().strip()
print(f"[INFO] Bitwarden 패스워드 파일 읽음: {pw_file}")

# ===== 3. Bitwarden CLI unlock (세션 토큰 획득) =====
try:
    bw_session = subprocess.check_output(
        ["bw", "unlock", bw_password, "--raw"], text=True
    ).strip()
    print(f"[INFO] Bitwarden 세션 토큰 획득 (앞부분): {bw_session[:6]}...")
except Exception as e:
    print(f"[ERROR] Bitwarden unlock 실패: {e}")
    sys.exit(1)

# ===== 4. Bitwarden에서 'Vault Unseal Key' 항목 검색 및 언실키 추출 =====
try:
    bw_items = subprocess.check_output(
        ["bw", "list", "items", "--search", BW_ITEM, "--session", bw_session], text=True
    )
    items_json = json.loads(bw_items)
    if not items_json:
        print("[ERROR] Bitwarden에서 언실키 항목을 찾지 못했습니다.")
        sys.exit(1)
    fields = items_json[0].get("fields", [])
    keys = [f["value"] for f in fields if f["name"].startswith("Unseal Key") and f["value"]]
    print(f"[INFO] 추출된 언실키 개수: {len(keys)}")
    if not keys:
        print("[ERROR] Unseal Key가 없습니다.")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Bitwarden 항목 파싱 실패: {e}")
    sys.exit(1)

# ===== 5. Vault API에 순차적으로 언실키 입력 =====
for idx, key in enumerate(keys, 1):
    try:
        r = requests.put(f"{VAULT_ADDR}/v1/sys/unseal", json={"key": key}, verify=False)
        print(f"[INFO] ({idx}) Vault 언실 응답: {r.json()}")
    except Exception as e:
        print(f"[ERROR] ({idx}) Vault API 요청 실패: {e}")

print("[SUCCESS] Vault 자동 언실 완료")
