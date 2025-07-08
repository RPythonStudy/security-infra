# src/security_infra/auto_unseal.py

import subprocess
import json
import requests
import urllib3

def auto_unseal(
    bw_item="vault unseal key - desktop",
    vault_addr="https://127.0.0.1:8200",
    logger=print
):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    logger("[DEBUG] auto_unseal 함수 진입")

    try:
        bw_session = subprocess.check_output(['bw', 'unlock', '--raw']).decode().strip()
        logger(f"[DEBUG] bw_session: {bw_session[:5]}... (length={len(bw_session)})")
    except Exception as e:
        logger(f"[ERROR] bw unlock 실패: {e}")
        return

    try:
        bw_items = subprocess.check_output([
            'bw', 'list', 'items', '--search', bw_item, '--session', bw_session
        ])
        logger(f"[DEBUG] bw_items(raw, length={len(bw_items)}):\n{bw_items[:200]}...")
    except Exception as e:
        logger(f"[ERROR] bw list 실패: {e}")
        return

    try:
        items_json = json.loads(bw_items)
        logger(f"[DEBUG] items_json:\n{json.dumps(items_json, indent=2, ensure_ascii=False)}")
        if not items_json:
            logger("[ERROR] Bitwarden에서 항목을 찾지 못했습니다.")
            return
        fields = items_json[0].get('fields', [])
        logger("[DEBUG] fields:")
        for f in fields:
            val = f['value'] if f['value'] is not None else "(None)"
            logger(f"  - {f['name']}: {val[:8]}... (len={len(val) if val != '(None)' else 0})")
        keys = [f['value'] for f in fields if f['name'].startswith("Unseal Key") and f['value'] is not None]
        logger("[DEBUG] keys:")
        for idx, k in enumerate(keys, 1):
            logger(f"  {idx}: {k[:8]}... (len={len(k)})")
    except Exception as e:
        logger(f"[ERROR] bw_items 파싱 실패: {e}")
        return

    logger(f"[INFO] 추출된 키 개수: {len(keys)}")
    if not keys:
        logger("[ERROR] Unseal Key를 찾을 수 없습니다. BW 필드명을 확인하세요.")
        return

    for idx, key in enumerate(keys, 1):
        logger(f"[INFO] ({idx}) vault 언실 시도...")
        try:
            r = requests.put(f"{vault_addr}/v1/sys/unseal", json={"key": key}, verify=False)
            try:
                logger(f"[RESULT] {json.dumps(r.json(), indent=2, ensure_ascii=False)}")
            except Exception:
                logger(f"[ERROR] {r.status_code} {r.reason}: {r.text}")
        except Exception as e:
            logger(f"[ERROR] ({idx}) vault 요청 실패: {e}")

    logger("[DEBUG] auto_unseal 함수 종료")
    logger("[SUCCESS] Vault auto-unseal 완료!")

if __name__ == "__main__":
    auto_unseal()
