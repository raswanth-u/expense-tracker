# backup/config.py
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from functools import lru_cache
from datetime import datetime
from enum import Enum

class BackupFormat(str, Enum):
    """Backup format types"""
    SQL = "sql"  # Plain SQL dump
    CUSTOM = "custom"  # PostgreSQL custom format (compressed)
    DIRECTORY = "directory"  # Directory format
    TAR = "tar"  # Tar archive

class CompressionLevel(int, Enum):
    """Compression levels for backups"""
    NONE = 0
    FAST = 1
    DEFAULT = 6
    BEST = 9

class BackupSettings(BaseSettings):
    """Backup configuration settings"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="BACKUP_",
        extra="ignore"
    )
    
    # Database settings (inherited from main config)
    database_user: str
    database_port: int
    database_password: str
    database_name: str
    database_host: str
    
    # Backup specific settings
    backup_dir: Path = Field(default=Path("backups"))
    backup_format: BackupFormat = BackupFormat.CUSTOM
    compression_level: CompressionLevel = CompressionLevel.DEFAULT
    
    # Retention settings
    keep_daily: int = Field(default=7, description="Keep daily backups for N days")
    keep_weekly: int = Field(default=4, description="Keep weekly backups for N weeks")
    keep_monthly: int = Field(default=6, description="Keep monthly backups for N months")
    
    # Advanced settings
    parallel_jobs: int = Field(default=4, ge=1, le=16)
    verbose: bool = False
    
    @property
    def pg_connection_string(self) -> str:
        """PostgreSQL connection string"""
        return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"

@lru_cache()
def get_backup_settings() -> BackupSettings:
    return BackupSettings()