# cli/menus/expense_menu.py
from cli.client import client
from cli.display import (
    display_menu, display_expense_table, display_expense_details,
    display_expense_statistics, display_monthly_summary, display_savings_account_table,
    display_user_table, display_debit_card_table, display_credit_card_table,
    get_input, print_success, print_error, print_header, console
)
from cli.config import setup_cli_logging
from datetime import datetime

logger = setup_cli_logging()

def expense_menu():
    """Expense management menu"""
    logger.info("Entered expense menu")
    
    while True:
        choice = display_menu(
            "Expense Management",
            [
                "Create Expense",
                "List All Expenses",
                "List Expenses by User",
                "View Expense Details",
                "Filter Expenses (Advanced)",
                "Update Expense",
                "Delete Expense",
                "View Statistics",
                "Monthly Summary"
            ]
        )
        
        if choice == "0":
            logger.info("Exiting expense menu")
            break
        elif choice == "1":
            create_expense()
        elif choice == "2":
            list_all_expenses()
        elif choice == "3":
            list_expenses_by_user()
        elif choice == "4":
            view_expense_details()
        elif choice == "5":
            filter_expenses()
        elif choice == "6":
            update_expense()
        elif choice == "7":
            delete_expense()
        elif choice == "8":
            view_statistics()
        elif choice == "9":
            monthly_summary()
        else:
            print_error("Invalid option. Please try again.")

def create_expense():
    """Create a new expense"""
    print_header("Create Expense")
    logger.info("Creating new expense")
    
    # Select user
    response = client.get_users()
    if not response:
        return
    
    users = response.get("users", [])
    if not users:
        print_error("No users found.")
        return
    
    display_user_table(users)
    
    try:
        user_choice = int(get_input("\nSelect user (S.No)"))
        if not (1 <= user_choice <= len(users)):
            print_error("Invalid selection.")
            return
        
        user_id = users[user_choice - 1]["id"]
        
        # Category
        console.print("\n[yellow]Categories:[/yellow]")
        categories = [
            "food", "transportation", "utilities", "entertainment",
            "shopping", "healthcare", "education", "travel",
            "rent", "groceries", "other"
        ]
        for idx, cat in enumerate(categories, 1):
            console.print(f"  {idx}. {cat.title()}")
        
        cat_choice = int(get_input("Select category (1-11)"))
        if not (1 <= cat_choice <= len(categories)):
            print_error("Invalid category.")
            return
        
        category = categories[cat_choice - 1]
        
        # Amount
        amount = float(get_input("Amount ($)"))
        if amount <= 0:
            print_error("Amount must be positive.")
            return
        
        # Payment method
        console.print("\n[yellow]Payment Methods:[/yellow]")
        console.print("  1. Debit Card")
        console.print("  2. Credit Card")
        console.print("  3. Cash")
        console.print("  4. UPI")
        console.print("  5. Net Banking")
        
        method_choice = get_input("Select payment method (1-5)")
        methods = {
            "1": "debit_card",
            "2": "credit_card",
            "3": "cash",
            "4": "upi",
            "5": "net_banking"
        }
        
        if method_choice not in methods:
            print_error("Invalid payment method.")
            return
        
        payment_method = methods[method_choice]
        
        # Handle card selection if needed
        debit_card_id = None
        credit_card_id = None
        savings_account_id = None
        
        if payment_method == "debit_card":
            console.print("\n[cyan]Select Debit Card:[/cyan]")
            cards_response = client.get_debit_cards(user_id=user_id)
            if not cards_response:
                return
            
            cards = cards_response.get("cards", [])
            if not cards:
                print_error("User has no debit cards.")
                return
            
            display_debit_card_table(cards)
            
            card_choice = int(get_input("\nSelect card (S.No)"))
            if not (1 <= card_choice <= len(cards)):
                print_error("Invalid selection.")
                return
            
            debit_card_id = cards[card_choice - 1]["id"]
        
        elif payment_method == "credit_card":
            console.print("\n[cyan]Select Credit Card:[/cyan]")
            cards_response = client.get_credit_cards(user_id=user_id)
            if not cards_response:
                return
            
            cards = cards_response.get("cards", [])
            if not cards:
                print_error("User has no credit cards.")
                return
            
            display_credit_card_table(cards)
            
            card_choice = int(get_input("\nSelect card (S.No)"))
            if not (1 <= card_choice <= len(cards)):
                print_error("Invalid selection.")
                return
            
            credit_card_id = cards[card_choice - 1]["id"]
            
        elif payment_method in ["upi", "net_banking"]:
            console.print("\n[cyan]Select Savings Account:[/cyan]")
            accounts_response = client.get_savings_accounts(user_id=user_id)
            if not accounts_response:
                return
            
            accounts = accounts_response.get("accounts", [])
            if not accounts:
                print_error("User has no savings accounts.")
                return
            
            display_savings_account_table(accounts)
            
            account_choice = int(get_input("\nSelect account (S.No)"))
            if not (1 <= account_choice <= len(accounts)):
                print_error("Invalid selection.")
                return
            
            savings_account_id = accounts[account_choice - 1]["id"]
        
        # Optional fields
        console.print("\n[bold cyan]Optional Information[/bold cyan]")
        merchant_name = get_input("Merchant name (optional)", required=False)
        description = get_input("Description (optional)", required=False)
        tags = get_input("Tags (optional)", required=False)
        
        expense_date_str = get_input("Expense date YYYY-MM-DD (default: today)", required=False)
        expense_date = None
        if expense_date_str:
            try:
                expense_date = datetime.strptime(expense_date_str, "%Y-%m-%d").isoformat()
            except ValueError:
                print_error("Invalid date format.")
                return
        
        # Create expense
        logger.info(
            f"Creating expense: user={user_id}, category={category}, "
            f"amount=${amount}, method={payment_method}"
        )
        
        expense_data = {
            "user_id": user_id,
            "category": category,
            "amount": amount,
            "payment_method": payment_method,
            "merchant_name": merchant_name or None,
            "description": description or None,
            "tags": tags or None
        }
        
        if debit_card_id:
            expense_data["debit_card_id"] = debit_card_id
        if credit_card_id:
            expense_data["credit_card_id"] = credit_card_id
        if expense_date:
            expense_data["expense_date"] = expense_date
        if savings_account_id:
            expense_data["savings_account_id"] = savings_account_id
        
        expense = client.create_expense(**expense_data)
        
        if expense:
            logger.info(f"Expense created: ID={expense['id']}")
            print_success(f"Expense created successfully! ID: {expense['id']}")
            console.print(f"[cyan]Category:[/cyan] {expense['category']}")
            console.print(f"[cyan]Amount:[/cyan] ${float(expense['amount']):,.2f}")
            console.print(f"[cyan]Method:[/cyan] {expense['payment_method']}")
            input("\nPress Enter to continue...")
    
    except ValueError as e:
        logger.error(f"Validation error in create_expense: {str(e)}")
        print_error(f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error in create_expense: {str(e)}", exc_info=True)
        print_error(f"An error occurred: {str(e)}")

def list_all_expenses():
    """List all expenses"""
    print_header("All Expenses")
    logger.debug("Listing all expenses")
    
    all_expenses = []
    response = None
    while True:
        response = client.get_expenses(limit=100)
        if not response:
            break
        
        expenses = response.get("expenses", [])
        if not expenses:
            break
        
        all_expenses.extend(expenses)
        skip = len(all_expenses)
        if skip >= response.get("total", 0):
            break
        
    if len(all_expenses):
        # expenses = response.get("expenses", [])
        display_expense_table(all_expenses)
        
        if all_expenses:
            total = sum(float(e['amount']) for e in all_expenses)
            console.print(f"\n[cyan]Showing {len(all_expenses)} of {response.get('total', 0)} expenses[/cyan]")
            console.print(f"[cyan]Total (shown):[/cyan] ${total:,.2f}")
        
        input("\nPress Enter to continue...")

def list_expenses_by_user():
    """List expenses for a user"""
    print_header("List Expenses by User")
    
    response = client.get_users()
    if not response:
        return
    
    users = response.get("users", [])
    if not users:
        print_error("No users found.")
        return
    
    display_user_table(users)
    
    try:
        choice = int(get_input("\nSelect user (S.No)"))
        if 1 <= choice <= len(users):
            user_id = users[choice - 1]["id"]
            logger.debug(f"Fetching expenses for user_id: {user_id}")
            
            all_expenses, response = _get_all_expenses(user_id=user_id)
            if len(all_expenses):
                expenses = all_expenses
                display_expense_table(expenses)
                
                if expenses:
                    total = sum(float(e['amount']) for e in expenses)
                    console.print(f"\n[cyan]Total expenses:[/cyan] {response.get('total', 0)}")
                    console.print(f"[cyan]Total amount (shown):[/cyan] ${total:,.2f}")
                
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def view_expense_details():
    """View detailed expense information"""
    print_header("View Expense Details")
    
    response = client.get_expenses(limit=50)
    if not response:
        return
    
    expenses = response.get("expenses", [])
    if not expenses:
        print_error("No expenses found.")
        return
    
    display_expense_table(expenses)
    
    try:
        choice = int(get_input("\nSelect expense (S.No)"))
        if 1 <= choice <= len(expenses):
            expense_id = expenses[choice - 1]["id"]
            logger.debug(f"Fetching details for expense_id: {expense_id}")
            
            expense = client.get_expense_details(expense_id)
            if expense:
                display_expense_details(expense)
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def _get_all_expenses(batch_size=100, **kwargs):
    all_expenses = []
    response = None
    skip = 0
    
    while True:
        response = client.get_expenses(skip=skip, limit=batch_size, **kwargs)
        if not response:
            break
            
        expenses = response.get("expenses", [])
        if not expenses:
            break
            
        all_expenses.extend(expenses)
        skip += batch_size
        
        # Check if we've got all expenses
        total = response.get("total", 0)
        if len(all_expenses) >= total:
            break
    
    return all_expenses, response

def filter_expenses():
    """Advanced expense filtering"""
    print_header("Filter Expenses")
    logger.debug("Advanced expense filtering")
    
    console.print("[yellow]Enter filter criteria (leave blank to skip):[/yellow]\n")
    
    # Category filter
    category = None
    cat_input = get_input("Category (food/shopping/etc.)", required=False)
    if cat_input:
        category = cat_input.lower()
    
    # Payment method filter
    payment_method = None
    method_input = get_input("Payment method (debit_card/credit_card/cash/upi/net_banking)", required=False)
    if method_input:
        payment_method = method_input.lower()
    
    # Date range
    start_date = get_input("Start date (YYYY-MM-DD)", required=False)
    end_date = get_input("End date (YYYY-MM-DD)", required=False)
    
    # Amount range
    min_amount = get_input("Minimum amount", required=False)
    max_amount = get_input("Maximum amount", required=False)
    
    try:
        all_expenses, response = _get_all_expenses(
            category=category,
            payment_method=payment_method,
            start_date=start_date or None,
            end_date=end_date or None,
            min_amount=float(min_amount) if min_amount else None,
            max_amount=float(max_amount) if max_amount else None
        )
        # response = client.get_expenses(
        #     category=category,
        #     payment_method=payment_method,
        #     start_date=start_date or None,
        #     end_date=end_date or None,
        #     min_amount=float(min_amount) if min_amount else None,
        #     max_amount=float(max_amount) if max_amount else None,
        #     limit=100
        # )
        
        if len(all_expenses):
            expenses = all_expenses
            display_expense_table(expenses)
            
            if expenses:
                total = sum(float(e['amount']) for e in expenses)
                console.print(f"\n[cyan]Found {response.get('total', 0)} expenses[/cyan]")
                console.print(f"[cyan]Total amount:[/cyan] ${total:,.2f}")
            
            input("\nPress Enter to continue...")
    except Exception as e:
        logger.error(f"Error in filter_expenses: {str(e)}", exc_info=True)
        print_error(f"An error occurred: {str(e)}")

def update_expense():
    """Update expense"""
    print_header("Update Expense")
    
    response = client.get_expenses(limit=50)
    if not response:
        return
    
    expenses = response.get("expenses", [])
    if not expenses:
        print_error("No expenses found.")
        return
    
    display_expense_table(expenses)
    
    try:
        choice = int(get_input("\nSelect expense (S.No)"))
        if 1 <= choice <= len(expenses):
            expense_id = expenses[choice - 1]["id"]
            
            console.print("\n[yellow]Leave fields empty to keep current value[/yellow]")
            console.print("[yellow]Note: Amount, date, and payment method cannot be changed[/yellow]\n")
            
            # Get update data
            description = get_input("New description (press Enter to skip)", required=False)
            merchant_name = get_input("New merchant name (press Enter to skip)", required=False)
            tags = get_input("New tags (press Enter to skip)", required=False)
            
            update_data = {}
            
            if description:
                update_data["description"] = description
            if merchant_name:
                update_data["merchant_name"] = merchant_name
            if tags:
                update_data["tags"] = tags
            
            if update_data:
                logger.info(f"Updating expense {expense_id}")
                expense = client.update_expense(expense_id, **update_data)
                if expense:
                    print_success("Expense updated successfully!")
                    display_expense_details(expense)
                    input("\nPress Enter to continue...")
            else:
                print_error("No fields to update.")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def delete_expense():
    """Delete expense"""
    print_header("Delete Expense")
    
    console.print("[red]⚠ WARNING: Deleting an expense does NOT reverse financial transactions![/red]")
    console.print("[yellow]This operation should be used carefully.[/yellow]\n")
    
    response = client.get_expenses(limit=50)
    if not response:
        return
    
    expenses = response.get("expenses", [])
    if not expenses:
        print_error("No expenses found.")
        return
    
    display_expense_table(expenses)
    
    try:
        choice = int(get_input("\nSelect expense (S.No)"))
        if 1 <= choice <= len(expenses):
            expense_id = expenses[choice - 1]["id"]
            expense = expenses[choice - 1]
            
            console.print(f"\n[yellow]Expense:[/yellow] {expense['category']} - ${float(expense['amount']):,.2f}")
            confirm = get_input("Are you sure you want to delete this expense? (yes/no)")
            
            if confirm.lower() in ["yes", "y"]:
                logger.warning(f"Deleting expense {expense_id}")
                if client.delete_expense(expense_id):
                    print_success("Expense deleted successfully!")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def view_statistics():
    """View expense statistics"""
    print_header("Expense Statistics")
    
    # Select user
    response = client.get_users()
    if not response:
        return
    
    users = response.get("users", [])
    if not users:
        print_error("No users found.")
        return
    
    display_user_table(users)
    
    try:
        choice = int(get_input("\nSelect user (S.No)"))
        if 1 <= choice <= len(users):
            user_id = users[choice - 1]["id"]
            
            # Optional date range
            console.print("\n[yellow]Date Range (optional):[/yellow]")
            start_date = get_input("Start date (YYYY-MM-DD)", required=False)
            end_date = get_input("End date (YYYY-MM-DD)", required=False)
            
            logger.debug(f"Getting statistics for user {user_id}")
            
            stats = client.get_expense_statistics(
                user_id=user_id,
                start_date=start_date or None,
                end_date=end_date or None
            )
            
            if stats:
                display_expense_statistics(stats)
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def monthly_summary():
    """View monthly expense summary"""
    print_header("Monthly Summary")
    
    # Select user
    response = client.get_users()
    if not response:
        return
    
    users = response.get("users", [])
    if not users:
        print_error("No users found.")
        return
    
    display_user_table(users)
    
    try:
        choice = int(get_input("\nSelect user (S.No)"))
        if 1 <= choice <= len(users):
            user_id = users[choice - 1]["id"]
            
            # Get year and month
            year = int(get_input("Year (e.g., 2024)"))
            month = int(get_input("Month (1-12)"))
            
            if not (1 <= month <= 12):
                print_error("Month must be between 1 and 12.")
                return
            
            logger.debug(f"Getting monthly summary for user {user_id}, {year}-{month:02d}")
            
            summary = client.get_monthly_summary(user_id, year, month)
            
            if summary:
                display_monthly_summary(summary)
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input. Please enter valid numbers.")