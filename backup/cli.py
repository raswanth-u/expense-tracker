# backup/cli.py
#!/usr/bin/env python3
"""
Database backup and restore CLI
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from backup.manager import BackupManager
from backup.config import BackupFormat

console = Console()

def create_backup_command(args):
    """Create a backup"""
    console.print("[bold cyan]Creating database backup...[/bold cyan]\n")
    
    manager = BackupManager()
    
    try:
        backup_path = manager.create_backup(
            backup_name=args.name,
            format_override=BackupFormat(args.format) if args.format else None
        )
        
        console.print(f"\n[green]✅ Backup created successfully![/green]")
        console.print(f"[cyan]Location:[/cyan] {backup_path}")
        
    except Exception as e:
        console.print(f"[red]❌ Backup failed: {e}[/red]")
        sys.exit(1)

def restore_backup_command(args):
    """Restore a backup"""
    backup_path = Path(args.backup_path)
    
    if not backup_path.exists():
        console.print(f"[red]❌ Backup file not found: {backup_path}[/red]")
        sys.exit(1)
    
    # Warning prompt
    if not args.yes:
        console.print("[yellow]⚠️  WARNING: This will overwrite the current database![/yellow]")
        console.print(f"[yellow]Database: {args.backup_path}[/yellow]")
        
        response = console.input("\n[bold]Continue? (yes/no): [/bold]")
        if response.lower() not in ['yes', 'y']:
            console.print("[yellow]Restore cancelled.[/yellow]")
            return
    
    console.print("\n[bold cyan]Restoring database...[/bold cyan]\n")
    
    manager = BackupManager()
    
    try:
        manager.restore_backup(
            backup_path=backup_path,
            drop_existing=args.drop,
            verify_checksum=not args.no_verify
        )
        
        console.print("\n[green]✅ Database restored successfully![/green]")
        
    except Exception as e:
        console.print(f"\n[red]❌ Restore failed: {e}[/red]")
        sys.exit(1)

def list_backups_command(args):
    """List all backups"""
    manager = BackupManager()
    backups = manager.list_backups()
    
    if not backups:
        console.print("[yellow]No backups found.[/yellow]")
        return
    
    table = Table(title="Available Backups", box=box.ROUNDED)
    table.add_column("Index", style="cyan", justify="right")
    table.add_column("Filename", style="green")
    table.add_column("Date", style="blue")
    table.add_column("Size", style="yellow", justify="right")
    table.add_column("Format", style="magenta")
    table.add_column("Checksum", style="dim")
    
    for idx, backup in enumerate(backups, 1):
        table.add_row(
            str(idx),
            backup.filename,
            backup.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            manager._format_size(backup.size_bytes),
            backup.format.upper(),
            backup.checksum[:8] + "..."
        )
    
    console.print(table)
    console.print(f"\n[cyan]Total backups:[/cyan] {len(backups)}")
    
    total_size = sum(b.size_bytes for b in backups)
    console.print(f"[cyan]Total size:[/cyan] {manager._format_size(total_size)}")

def verify_backup_command(args):
    """Verify a backup"""
    backup_path = Path(args.backup_path)
    
    console.print(f"[cyan]Verifying backup:[/cyan] {backup_path}\n")
    
    manager = BackupManager()
    
    if manager.verify_backup(backup_path):
        console.print("[green]✅ Backup is valid[/green]")
    else:
        console.print("[red]❌ Backup verification failed[/red]")
        sys.exit(1)

def cleanup_command(args):
    """Clean up old backups"""
    console.print("[cyan]Cleaning up old backups...[/cyan]\n")
    
    manager = BackupManager()
    deleted_count = manager.cleanup_old_backups()
    
    if deleted_count > 0:
        console.print(f"[green]✅ Deleted {deleted_count} old backup(s)[/green]")
    else:
        console.print("[yellow]No old backups to delete[/yellow]")

def info_command(args):
    """Show backup system information"""
    manager = BackupManager()
    settings = manager.settings
    
    info = f"""
[cyan]Database:[/cyan] {settings.database_name}
[cyan]Host:[/cyan] {settings.database_host}:{settings.database_port}
[cyan]Backup Directory:[/cyan] {settings.backup_dir.absolute()}
[cyan]Default Format:[/cyan] {settings.backup_format.value.upper()}
[cyan]Compression Level:[/cyan] {settings.compression_level.value}

[yellow]Retention Policy:[/yellow]
[cyan]Daily:[/cyan] {settings.keep_daily} days
[cyan]Weekly:[/cyan] {settings.keep_weekly} weeks
[cyan]Monthly:[/cyan] {settings.keep_monthly} months
    """
    
    console.print(Panel(info, title="[bold]Backup System Information[/bold]", border_style="cyan"))

def main():
    parser = argparse.ArgumentParser(
        description="Database Backup & Restore System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create backup
    create_parser = subparsers.add_parser('create', help='Create a new backup')
    create_parser.add_argument('-n', '--name', help='Custom backup name')
    create_parser.add_argument(
        '-f', '--format',
        choices=['sql', 'custom', 'directory', 'tar'],
        help='Backup format'
    )
    create_parser.set_defaults(func=create_backup_command)
    
    # Restore backup
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('backup_path', help='Path to backup file')
    restore_parser.add_argument('-d', '--drop', action='store_true', help='Drop existing database')
    restore_parser.add_argument('--no-verify', action='store_true', help='Skip checksum verification')
    restore_parser.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompt')
    restore_parser.set_defaults(func=restore_backup_command)
    
    # List backups
    list_parser = subparsers.add_parser('list', help='List all backups')
    list_parser.set_defaults(func=list_backups_command)
    
    # Verify backup
    verify_parser = subparsers.add_parser('verify', help='Verify backup integrity')
    verify_parser.add_argument('backup_path', help='Path to backup file')
    verify_parser.set_defaults(func=verify_backup_command)
    
    # Cleanup old backups
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old backups')
    cleanup_parser.set_defaults(func=cleanup_command)
    
    # Show info
    info_parser = subparsers.add_parser('info', help='Show backup system information')
    info_parser.set_defaults(func=info_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)

if __name__ == "__main__":
    main()