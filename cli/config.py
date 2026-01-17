# cli/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import logging
from pathlib import Path

class CLISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore'
    )
    
    api_key: str
    api_base_url: str = "http://localhost:8000/api/v1"
    log_level: str = "INFO"
    log_dir: str = "logs"

@lru_cache()
def get_cli_settings() -> CLISettings:
    return CLISettings()

def setup_cli_logging() -> logging.Logger:
    """Setup CLI logging"""
    settings = get_cli_settings()
    
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger("cli")
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    if logger.handlers:
        return logger
    
    # File handler only (console output is handled by rich)
    file_handler = logging.FileHandler(
        log_dir / "cli.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

if __name__ == "__main__":
    s = get_cli_settings()
    print(s.api_key)
    print(s.api_base_url)