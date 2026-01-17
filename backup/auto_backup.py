# backup/auto_backup.py
#!/usr/bin/env python3
"""
Automated backup script for scheduled execution
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

from backup.manager import BackupManager
from backup.config import get_backup_settings

# Set up logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "backup.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_automated_backup():
    """Run automated backup with cleanup"""
    logger.info("="*60)
    logger.info("Starting automated backup")
    logger.info("="*60)
    
    settings = get_backup_settings()
    manager = BackupManager()
    
    try:
        # Create backup
        logger.info("Creating backup...")
        backup_path = manager.create_backup()
        logger.info(f"✅ Backup created: {backup_path}")
        
        # Verify backup
        logger.info("Verifying backup...")
        if not manager.verify_backup(backup_path):
            logger.error("❌ Backup verification failed!")
            sys.exit(1)
        logger.info("✅ Backup verified")
        
        # Cleanup old backups
        logger.info("Cleaning up old backups...")
        deleted_count = manager.cleanup_old_backups()
        logger.info(f"✅ Cleaned up {deleted_count} old backup(s)")
        
        # Summary
        backups = manager.list_backups()
        total_size = sum(b.size_bytes for b in backups)
        
        logger.info("="*60)
        logger.info("Backup Summary")
        logger.info("="*60)
        logger.info(f"Total backups: {len(backups)}")
        logger.info(f"Total size: {manager._format_size(total_size)}")
        logger.info(f"Latest backup: {backup_path.name}")
        logger.info("="*60)
        logger.info("✅ Automated backup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Automated backup failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_automated_backup()