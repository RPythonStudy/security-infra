import os
import subprocess
from security_infra.usb_utils import find_usb_mount_by_label

# 1. 현재 블록 디바이스 상태 출력
print("\n==== [DEBUG] lsblk 출력 ====")
os.system("lsblk -o NAME,LABEL,SIZE,MOUNTPOINT")

# 2. 마운트된 USB 디렉토리 내용 확인
print("\n==== [DEBUG] /mnt/usb 내용 ====")
os.system("ls -l /mnt/usb || echo '[INFO] /mnt/usb 없음'")

# 3. usb_utils 직접 호출 및 추가 디버깅
usb_mount = find_usb_mount_by_label("BW_PW_USB", test_file="bt_pw_user1.enc")

if usb_mount:
    print(f"[INFO] USB mount point: {usb_mount}")
else:
    print("[ERROR] USB not detected")

