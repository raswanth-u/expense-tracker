# requirements_backup.txt

    pydantic>=2.0.0
    pydantic-settings>=2.0.0
    rich>=13.0.0
    python-crontab>=3.0.0

# Usage Examples
# 1. Create Backup

        # Basic backup
        python -m backup.cli create

        # Custom name
        python -m backup.cli create -n "before_migration"

        # Specific format
        python -m backup.cli create -f sql

        # Directory format (parallel)
        python -m backup.cli create -f directory

# 2. List Backups

    python -m backup.cli list

# 3. Restore Backup

        # Restore with confirmation
        python -m backup.cli restore backups/backup_mydb_20240101_120000.dump

        # Auto-confirm
        python -m backup.cli restore backups/backup_mydb_20240101_120000.dump -y

        # Drop and recreate database
        python -m backup.cli restore backups/backup_mydb_20240101_120000.dump -d -y

        # Skip checksum verification (faster)
        python -m backup.cli restore backups/backup_mydb_20240101_120000.dump --no-verify

# 4. Verify Backup

    python -m backup.cli verify backups/backup_mydb_20240101_120000.dump

# 5. Cleanup Old Backups

    python -m backup.cli cleanup

# 6. Show Info

    python -m backup.cli info

# 7. Setup Automated Backups

        # Install cron job
        python scripts/setup_cron.py

        # Or manually run automated backup
        python backup/auto_backup.py