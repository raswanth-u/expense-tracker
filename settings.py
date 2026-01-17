# config.py
import logging
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    database_user: str
    database_port: int
    database_password: str
    database_name: str
    database_host: str
    api_key: str
    
    # Logging settings
    log_level: str = "INFO"
    log_dir: str = "logs"
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
        
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Logging configuration
def setup_logging(name: str, log_file: str | None = None) -> logging.Logger:
    """Setup logging with file and console handlers"""
    settings = get_settings()
    
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(levelname)s - %(message)s'
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.log_level.upper()))
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file specified)
    if log_file:
        file_handler = logging.FileHandler(
            log_dir / log_file,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, settings.log_level.upper()))
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger
    

if(__name__ == "__main__"):
    # Create an instance
    settings = Settings(database_user="admin")

    # Now you can access the values
    postgres_url = f"postgresql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"
    print(postgres_url)
    
    s = get_settings()