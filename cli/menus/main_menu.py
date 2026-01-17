# cli/menus/main_menu.py
from cli.display import display_menu, print_error, console
from cli.menus.user_menu import user_menu
from cli.menus.savings_menu import savings_menu
from cli.menus.debit_card_menu import debit_card_menu
from cli.menus.credit_card_menu import credit_card_menu
from cli.menus.expense_menu import expense_menu
from cli.config import setup_cli_logging

logger = setup_cli_logging()

def main_menu():
    """Main application menu"""
    logger.info("Application started")
    
    while True:
        choice = display_menu(
            "Expense Tracker CLI",
            [
                "User Management",
                "Savings Accounts",
                "Debit Cards",
                "Credit Cards",
                "Expenses"
            ]
        )
        
        if choice == "0":
            logger.info("Application closing")
            console.print("\n[green]👋 Goodbye![/green]")
            break
        elif choice == "1":
            user_menu()
        elif choice == "2":
            savings_menu()
        elif choice == "3":
            debit_card_menu()
        elif choice == "4":
            credit_card_menu()
        elif choice == "5":
            expense_menu()
        else:
            print_error("Invalid option. Please try again.")