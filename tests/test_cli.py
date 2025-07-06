import pytest
import sys
from typer.testing import CliRunner
from pathlib import Path
import shutil
import os

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.security_infra import app




runner = CliRunner()

@pytest.fixture
def tmp_project(tmp_path):
    # 가짜 프로젝트 구조 생성
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(orig_cwd)

def test_init_folders_creates_dirs(tmp_project):
    # 임시 프로젝트 구조 내에서 폴더 생성
    result = runner.invoke(app, ["init-folders", "--base-dir", str(tmp_project)])
    assert result.exit_code == 0
    # 주요 폴더가 실제로 생성됐는지 확인
    required_dirs = [
        "docker/elk/esdata",
        "docker/elk/logstash/pipeline",
        "docker/keycloak/data",
        "docker/vault/config",
        "docker/vault/file",
        "docker/vault/certs",
        "docker/vault/logs",
        "docker/openldap/data",
        "docker/openldap/config",
    ]
    for rel in required_dirs:
        assert (tmp_project / rel).exists(), f"{rel} 폴더 미생성"

def test_init_folders_skip_existing(tmp_project):
    # 폴더를 미리 만들어둔 뒤 재실행
    test_dir = tmp_project / "docker/elk/esdata"
    test_dir.mkdir(parents=True)
    result = runner.invoke(app, ["init-folders", "--base-dir", str(tmp_project)])
    assert "[스킵]" in result.output

def test_show_install_history_no_log(tmp_project):
    # 로그 파일이 없을 때 예외
    result = runner.invoke(app, ["show-install-history", "--project-logfile", str(tmp_project / "logs/install.log")])
    assert "로그 파일이 없습니다." in result.output

def test_show_install_history(tmp_project):
    # 감사 로그 파일을 생성해두고 테스트
    log_path = tmp_project / "logs/install.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("테스트로그1\n테스트로그2\n테스트로그3\n")
    result = runner.invoke(app, ["show-install-history", "--project-logfile", str(log_path), "--last", "2"])
    assert "---" in result.output
    assert "테스트로그2" in result.output
    assert "테스트로그3" in result.output

def test_main_callback_sets_exec_id(monkeypatch):
    # 환경변수, 로그레벨 등 정상 실행 확인
    result = runner.invoke(app, ["init-folders"])
    assert result.exit_code == 0
    # PS_EXEC_UUID 환경변수가 설정되는지 확인
    assert "실행ID" in result.output

# sudo 등 시스템 권한 테스트는 생략/별도 마킹
