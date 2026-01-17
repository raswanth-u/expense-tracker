# backup/manager.py
import subprocess
import shutil
import gzip
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
from dataclasses import dataclass, asdict
import logging

from backup.config import get_backup_settings, BackupFormat

logger = logging.getLogger(__name__)

@dataclass
class BackupMetadata:
    """Metadata for a backup"""
    filename: str
    format: str
    size_bytes: int
    checksum: str
    created_at: datetime
    database_name: str
    database_version: Optional[str] = None
    compressed: bool = False
    tables_count: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BackupMetadata':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)

class BackupManager:
    """Manages database backups and restores"""
    
    def __init__(self):
        self.settings = get_backup_settings()
        self.backup_dir = self.settings.backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            level=logging.DEBUG if self.settings.verbose else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger.info(f"Backup directory: {self.backup_dir}")
    
    def create_backup(
        self,
        backup_name: Optional[str] = None,
        format_override: Optional[BackupFormat] = None
    ) -> Path:
        """
        Create a database backup
        
        Args:
            backup_name: Custom backup name (default: timestamp-based)
            format_override: Override default backup format
            
        Returns:
            Path to the backup file
        """
        logger.info("Starting database backup...")
        
        # Generate backup filename
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{self.settings.database_name}_{timestamp}"
        
        backup_format = format_override or self.settings.backup_format
        
        # Determine file extension
        extension_map = {
            BackupFormat.SQL: ".sql",
            BackupFormat.CUSTOM: ".dump",
            BackupFormat.DIRECTORY: "",
            BackupFormat.TAR: ".tar"
        }
        extension = extension_map[backup_format]
        backup_path = self.backup_dir / f"{backup_name}{extension}"
        
        # Build pg_dump command
        cmd = self._build_dump_command(backup_path, backup_format)
        
        try:
            # Execute backup
            logger.debug(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                env=self._get_env()
            )
            
            if result.stderr and self.settings.verbose:
                logger.debug(f"pg_dump output: {result.stderr}")
            
            # Compress if SQL format
            if backup_format == BackupFormat.SQL:
                backup_path = self._compress_backup(backup_path)
            
            # Calculate checksum
            checksum = self._calculate_checksum(backup_path)
            
            # Get database version
            db_version = self._get_database_version()
            
            # Create metadata
            metadata = BackupMetadata(
                filename=backup_path.name,
                format=backup_format.value,
                size_bytes=backup_path.stat().st_size,
                checksum=checksum,
                created_at=datetime.now(),
                database_name=self.settings.database_name,
                database_version=db_version,
                compressed=backup_format == BackupFormat.SQL
            )
            
            # Save metadata
            self._save_metadata(backup_path, metadata)
            
            logger.info(f"✅ Backup created successfully: {backup_path}")
            logger.info(f"📦 Size: {self._format_size(metadata.size_bytes)}")
            logger.info(f"🔒 Checksum: {checksum[:16]}...")
            
            return backup_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Backup failed: {e.stderr}")
            raise RuntimeError(f"Backup failed: {e.stderr}") from e
    
    def restore_backup(
        self,
        backup_path: Path | str,
        drop_existing: bool = False,
        verify_checksum: bool = True
    ) -> None:
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup file
            drop_existing: Drop existing database before restore
            verify_checksum: Verify backup integrity before restore
        """
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        logger.info(f"Starting database restore from: {backup_path}")
        
        # Load and verify metadata
        metadata = self._load_metadata(backup_path)
        if metadata and verify_checksum:
            logger.info("Verifying backup integrity...")
            if not self._verify_checksum(backup_path, metadata.checksum):
                raise ValueError("Backup file is corrupted (checksum mismatch)")
            logger.info("✅ Backup integrity verified")
        
        # Decompress if needed
        restore_path = backup_path
        if backup_path.suffix == ".gz":
            logger.info("Decompressing backup...")
            restore_path = self._decompress_backup(backup_path)
        
        try:
            # Drop existing database if requested
            if drop_existing:
                logger.warning("Dropping existing database...")
                self._drop_database()
                self._create_database()
            
            # Determine backup format
            backup_format = self._detect_backup_format(restore_path)
            
            # Build pg_restore/psql command
            cmd = self._build_restore_command(restore_path, backup_format)
            
            # Execute restore
            logger.debug(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=self._get_env()
            )
            
            # pg_restore returns non-zero for warnings, check stderr instead
            if result.returncode != 0 and "ERROR" in result.stderr:
                raise RuntimeError(f"Restore failed: {result.stderr}")
            
            if result.stderr and self.settings.verbose:
                logger.debug(f"Restore output: {result.stderr}")
            
            logger.info("✅ Database restored successfully")
            
        finally:
            # Clean up temporary decompressed file
            if restore_path != backup_path and restore_path.exists():
                restore_path.unlink()
    
    def list_backups(self) -> List[BackupMetadata]:
        """List all available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("backup_*"):
            if backup_file.suffix in [".sql", ".gz", ".dump", ".tar"] or backup_file.is_dir():
                metadata = self._load_metadata(backup_file)
                if metadata:
                    backups.append(metadata)
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x.created_at, reverse=True)
        return backups
    
    def cleanup_old_backups(self) -> int:
        """
        Clean up old backups based on retention policy
        
        Returns:
            Number of backups deleted
        """
        logger.info("Cleaning up old backups...")
        
        backups = self.list_backups()
        now = datetime.now()
        deleted_count = 0
        
        for backup in backups:
            age_days = (now - backup.created_at).days
            should_delete = False
            
            # Daily retention
            if age_days <= self.settings.keep_daily:
                continue
            
            # Weekly retention (keep one per week)
            elif age_days <= self.settings.keep_daily + (self.settings.keep_weekly * 7):
                # Keep if it's the first backup of the week
                week_start = backup.created_at - timedelta(days=backup.created_at.weekday())
                if not self._is_first_backup_of_period(backups, backup, week_start, timedelta(days=7)):
                    should_delete = True
            
            # Monthly retention (keep one per month)
            elif age_days <= self.settings.keep_daily + (self.settings.keep_weekly * 7) + (self.settings.keep_monthly * 30):
                # Keep if it's the first backup of the month
                month_start = backup.created_at.replace(day=1)
                if not self._is_first_backup_of_period(backups, backup, month_start, timedelta(days=30)):
                    should_delete = True
            
            # Delete if older than retention period
            else:
                should_delete = True
            
            if should_delete:
                backup_path = self.backup_dir / backup.filename
                metadata_path = self._get_metadata_path(backup_path)
                
                if backup_path.exists():
                    if backup_path.is_dir():
                        shutil.rmtree(backup_path)
                    else:
                        backup_path.unlink()
                    logger.info(f"Deleted old backup: {backup.filename}")
                    deleted_count += 1
                
                if metadata_path.exists():
                    metadata_path.unlink()
        
        logger.info(f"Cleaned up {deleted_count} old backup(s)")
        return deleted_count
    
    def verify_backup(self, backup_path: Path | str) -> bool:
        """
        Verify backup integrity
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if backup is valid
        """
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        # Load metadata
        metadata = self._load_metadata(backup_path)
        if not metadata:
            logger.warning("No metadata found for backup")
            return True  # Assume valid if no metadata
        
        # Verify checksum
        if not self._verify_checksum(backup_path, metadata.checksum):
            logger.error("❌ Checksum mismatch - backup is corrupted")
            return False
        
        logger.info("✅ Backup integrity verified")
        return True
    
    # Private methods
    
    def _build_dump_command(self, backup_path: Path, format: BackupFormat) -> List[str]:
        """Build pg_dump command"""
        cmd = [
            "pg_dump",
            "-h", self.settings.database_host,
            "-p", str(self.settings.database_port),
            "-U", self.settings.database_user,
            "-d", self.settings.database_name,
        ]
        
        # Format-specific options
        if format == BackupFormat.SQL:
            cmd.extend(["-f", str(backup_path)])
        elif format == BackupFormat.CUSTOM:
            cmd.extend([
                "-F", "c",
                "-f", str(backup_path),
                "-Z", str(self.settings.compression_level.value)
            ])
        elif format == BackupFormat.DIRECTORY:
            cmd.extend([
                "-F", "d",
                "-f", str(backup_path),
                "-j", str(self.settings.parallel_jobs)
            ])
        elif format == BackupFormat.TAR:
            cmd.extend(["-F", "t", "-f", str(backup_path)])
        
        if self.settings.verbose:
            cmd.append("-v")
        
        return cmd
    
    def _build_restore_command(self, backup_path: Path, format: BackupFormat) -> List[str]:
        """Build pg_restore or psql command"""
        if format == BackupFormat.SQL:
            # Use psql for SQL dumps
            cmd = [
                "psql",
                "-h", self.settings.database_host,
                "-p", str(self.settings.database_port),
                "-U", self.settings.database_user,
                "-d", self.settings.database_name,
                "-f", str(backup_path)
            ]
        else:
            # Use pg_restore for custom formats
            cmd = [
                "pg_restore",
                "-h", self.settings.database_host,
                "-p", str(self.settings.database_port),
                "-U", self.settings.database_user,
                "-d", self.settings.database_name,
                "-c",  # Clean (drop) database objects before recreating
            ]
            
            if format == BackupFormat.DIRECTORY:
                cmd.extend(["-j", str(self.settings.parallel_jobs)])
            
            if self.settings.verbose:
                cmd.append("-v")
            
            cmd.append(str(backup_path))
        
        return cmd
    
    def _get_env(self) -> dict:
        """Get environment variables for PostgreSQL commands"""
        import os
        env = os.environ.copy()
        env['PGPASSWORD'] = self.settings.database_password
        return env
    
    def _compress_backup(self, backup_path: Path) -> Path:
        """Compress backup file using gzip"""
        logger.info("Compressing backup...")
        compressed_path = backup_path.with_suffix(backup_path.suffix + ".gz")
        
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb', compresslevel=self.settings.compression_level.value) as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove original file
        backup_path.unlink()
        logger.info(f"Compressed: {backup_path.name} -> {compressed_path.name}")
        
        return compressed_path
    
    def _decompress_backup(self, backup_path: Path) -> Path:
        """Decompress gzipped backup file"""
        decompressed_path = backup_path.with_suffix("")
        
        with gzip.open(backup_path, 'rb') as f_in:
            with open(decompressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return decompressed_path
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    def _verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file checksum"""
        actual_checksum = self._calculate_checksum(file_path)
        return actual_checksum == expected_checksum
    
    def _get_metadata_path(self, backup_path: Path) -> Path:
        """Get metadata file path for backup"""
        return backup_path.with_suffix(backup_path.suffix + ".meta.json")
    
    def _save_metadata(self, backup_path: Path, metadata: BackupMetadata) -> None:
        """Save backup metadata"""
        metadata_path = self._get_metadata_path(backup_path)
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)
    
    def _load_metadata(self, backup_path: Path) -> Optional[BackupMetadata]:
        """Load backup metadata"""
        metadata_path = self._get_metadata_path(backup_path)
        
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r') as f:
                data = json.load(f)
                return BackupMetadata.from_dict(data)
        except Exception as e:
            logger.warning(f"Failed to load metadata: {e}")
            return None
    
    def _detect_backup_format(self, backup_path: Path) -> BackupFormat:
        """Detect backup format from file"""
        if backup_path.is_dir():
            return BackupFormat.DIRECTORY
        elif backup_path.suffix == ".sql":
            return BackupFormat.SQL
        elif backup_path.suffix == ".tar":
            return BackupFormat.TAR
        else:
            return BackupFormat.CUSTOM
    
    def _get_database_version(self) -> Optional[str]:
        """Get PostgreSQL version"""
        try:
            result = subprocess.run(
                [
                    "psql",
                    "-h", self.settings.database_host,
                    "-p", str(self.settings.database_port),
                    "-U", self.settings.database_user,
                    "-d", self.settings.database_name,
                    "-t",
                    "-c", "SELECT version();"
                ],
                capture_output=True,
                text=True,
                env=self._get_env()
            )
            return result.stdout.strip()
        except Exception:
            return None
    
    def _drop_database(self) -> None:
        """Drop database (use with caution!)"""
        subprocess.run(
            [
                "dropdb",
                "-h", self.settings.database_host,
                "-p", str(self.settings.database_port),
                "-U", self.settings.database_user,
                self.settings.database_name
            ],
            env=self._get_env(),
            check=True
        )
    
    def _create_database(self) -> None:
        """Create database"""
        subprocess.run(
            [
                "createdb",
                "-h", self.settings.database_host,
                "-p", str(self.settings.database_port),
                "-U", self.settings.database_user,
                self.settings.database_name
            ],
            env=self._get_env(),
            check=True
        )
    
    def _is_first_backup_of_period(
        self,
        all_backups: List[BackupMetadata],
        current_backup: BackupMetadata,
        period_start: datetime,
        period_length: timedelta
    ) -> bool:
        """Check if backup is the first in a given period"""
        period_end = period_start + period_length
        
        backups_in_period = [
            b for b in all_backups
            if period_start <= b.created_at < period_end
        ]
        
        if not backups_in_period:
            return False
        
        earliest = min(backups_in_period, key=lambda x: x.created_at)
        return earliest.filename == current_backup.filename
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"