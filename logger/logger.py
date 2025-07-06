# infra/logger/logger.py

import os
import sys
import logging
import logging.config
import yaml
from pathlib import Path

# 설정 상수
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEFAULT_LOG_CONFIG_PATH = Path("config/logging.yaml")
DEFAULT_LOG_FILE_PATH = Path("logs/dev.log")

# 내부 함수 1: 기본 설정
def setup_default_logging():
    log_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s - %(message)s")

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)

    DEFAULT_LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(DEFAULT_LOG_FILE_PATH, encoding="utf-8")
    file_handler.setFormatter(log_formatter)

    logging.basicConfig(
        level=DEFAULT_LOG_LEVEL,
        handlers=[stream_handler, file_handler]
    )

# 내부 함수 2: config.yaml 있으면 적용
def configure_logging():
    if DEFAULT_LOG_CONFIG_PATH.exists():
        with open(DEFAULT_LOG_CONFIG_PATH, "r") as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    else:
        setup_default_logging()

# 외부 제공 함수
def get_logger(name: str = "mathbank") -> logging.Logger:
    if not logging.getLogger().hasHandlers():
        configure_logging()
    return logging.getLogger(name)
