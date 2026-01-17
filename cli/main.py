# cli/main.py
# !/usr/bin/env python3
from cli.menus.main_menu import main_menu
from cli.display import console
from cli.config import setup_cli_logging

logger = setup_cli_logging()

def main():
    """CLI application entry point"""
    console.clear()
    
    # Display banner
    console.print("[bold green]" + "="*60 + "[/bold green]")
    console.print("[bold cyan]         EXPENSE TRACKER CLI - v1.0.0         [/bold cyan]")
    console.print("[bold green]" + "="*60 + "[/bold green]")
    console.print("[dim]Make sure the API server is running at http://localhost:8000[/dim]\n")
    
    logger.info("=== CLI Application Started ===")
    
    try:
        main_menu()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        console.print("\n\n👋 [yellow]Interrupted by user. Goodbye![/yellow]")
    except Exception as e:
        logger.error(f"Unhandled exception in main: {str(e)}", exc_info=True)
        console.print(f"\n[red]An error occurred: {e}[/red]")
    finally:
        logger.info("=== CLI Application Closed ===")

if __name__ == "__main__":
    main()