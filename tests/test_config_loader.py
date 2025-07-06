from security_infra_cli import config_loader
import pytest
from pathlib import Path
import tempfile
import yaml

SAMPLE_CONFIG = {
    "mode": "dev",
    "logging": {"level": "DEBUG"},
}

def write_temp_config(config_dict):
    tmp_dir = tempfile.TemporaryDirectory()
    config_path = Path(tmp_dir.name) / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_dict, f)
    return tmp_dir, config_path

def test_load_config_reads_file(monkeypatch):
    tmp_dir, config_path = write_temp_config(SAMPLE_CONFIG)
    monkeypatch.setattr(config_loader, "CONFIG_PATH", config_path)
    cfg = config_loader.load_config()
    assert cfg["mode"] == "dev"
    assert cfg["logging"]["level"] == "DEBUG"
    tmp_dir.cleanup()

def test_get_mode(monkeypatch):
    tmp_dir, config_path = write_temp_config({"mode": "education"})
    monkeypatch.setattr(config_loader, "CONFIG_PATH", config_path)
    cfg = config_loader.load_config()
    assert config_loader.get_mode(cfg) == "education"
    tmp_dir.cleanup()

def test_get_log_level(monkeypatch):
    tmp_dir, config_path = write_temp_config({"logging": {"level": "error"}})
    monkeypatch.setattr(config_loader, "CONFIG_PATH", config_path)
    cfg = config_loader.load_config()
    assert config_loader.get_log_level(cfg) == "ERROR"
    tmp_dir.cleanup()

def test_load_config_default(monkeypatch):
    monkeypatch.setattr(config_loader, "CONFIG_PATH", Path("/tmp/no/such/file.yml"))
    cfg = config_loader.load_config()
    assert isinstance(cfg, dict)

def test_get_mode_default():
    assert config_loader.get_mode({}) == "dev"

def test_get_log_level_default():
    assert config_loader.get_log_level({}) == "DEBUG"
