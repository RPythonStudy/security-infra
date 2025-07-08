# src/security_infra/auto_unseal.py

from dotenv import load_dotenv
import os
import subprocess

def connect_bitwarden():
    # 1. .env에서 환경변수 로딩
    load_dotenv()

    # 2. 환경변수 읽기
    BW_SERVER = os.getenv("BW_SERVER")
    BW_PASSWORD = os.getenv("BW_PASSWORD")

    # 3. Bitwarden 서버주소 CLI에 반영
    if BW_SERVER:
        subprocess.run(["bw", "config", "server", BW_SERVER], check=True)
        print(f"[INFO] Bitwarden 서버를 '{BW_SERVER}'로 설정했습니다.")
    else:
        print("[WARN] BW_SERVER 환경변수가 없습니다. (기본값 사용)")

    # 4. unlock 명령으로 세션 토큰 획득
    if BW_PASSWORD:
        try:
            bw_session = subprocess.check_output(
                ['bw', 'unlock', BW_PASSWORD, '--raw']
            ).decode().strip()
            print("[INFO] Bitwarden 세션 토큰을 성공적으로 획득했습니다.")
            return bw_session
        except Exception as e:
            print("[ERROR] bw unlock 실패:", e)
            return None
    else:
        print("[ERROR] 환경변수 BW_PASSWORD가 설정되어 있지 않습니다.")
        return None

if __name__ == "__main__":
    session = connect_bitwarden()
    if session:
        print("[SUCCESS] auto-unseal 준비 완료! (세션: 앞 8자)", session[:8])
    else:
        print("[FAIL] Bitwarden 세션 획득 실패.")
