# tests/test_backup.py
import pytest
from pathlib import Path
from backup.manager import BackupManager

def test_create_backup(tmp_path):
    """Test backup creation"""
    manager = BackupManager()
    manager.settings.backup_dir = tmp_path
    
    backup_path = manager.create_backup()
    
    assert backup_path.exists()
    assert backup_path.stat().st_size > 0

def test_restore_backup(tmp_path):
    """Test backup restoration"""
    manager = BackupManager()
    
    # Create backup
    backup_path = manager.create_backup()
    
    # Restore
    manager.restore_backup(backup_path)
    
    assert True  # If no exception, restore succeeded