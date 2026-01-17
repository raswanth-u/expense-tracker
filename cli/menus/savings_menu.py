# cli/menus/savings_menu.py
from cli.client import client
from cli.display import (
    display_menu, display_savings_account_table, display_savings_account_details,
    display_transaction_table, display_user_table, get_input, 
    print_success, print_error, print_header
)
from cli.utils import get_datetime_input

def savings_menu():
    """Savings account management menu"""
    while True:
        choice = display_menu(
            "Savings Account Management",
            [
                "Create Savings Account",
                "List All Accounts",
                "List Accounts by User",
                "View Account Details",
                "Update Account",
                "Delete Account",
                "Create Transaction (Deposit/Withdrawal)",
                "View Transactions"
            ]
        )
        
        if choice == "0":
            break
        elif choice == "1":
            create_account()
        elif choice == "2":
            list_all_accounts()
        elif choice == "3":
            list_accounts_by_user()
        elif choice == "4":
            view_account_details()
        elif choice == "5":
            update_account()
        elif choice == "6":
            delete_account()
        elif choice == "7":
            create_transaction()
        elif choice == "8":
            view_transactions()
        else:
            print_error("Invalid option. Please try again.")

def create_account():
    """Create a new savings account"""
    print_header("Create Savings Account")
    
    # First show users and let them select
    response = client.get_users()
    if not response:
        return
    
    users = response.get("users", [])
    if not users:
        print_error("No users found. Create a user first.")
        return
    
    display_user_table(users)
    
    try:
        user_choice = int(get_input("\nSelect user (S.No)"))
        if not (1 <= user_choice <= len(users)):
            print_error("Invalid selection.")
            return
        
        user_id = users[user_choice - 1]["id"]
        
        # Get account details
        account_name = get_input("Account name")
        bank_name = get_input("Bank name")
        account_number = get_input("Account number")
        account_type = get_input("Account type (savings/current)")
        minimum_balance = float(get_input("Minimum balance", required=False) or "0")
        current_balance = float(get_input("Current balance", required=False) or "0")
        interest_rate = float(get_input("Interest rate (%)", required=False) or "0")
        tags = get_input("Tags (optional)", required=False)
        
        account = client.create_savings_account(
            user_id=user_id,
            account_name=account_name,
            bank_name=bank_name,
            account_number=account_number,
            account_type=account_type,
            minimum_balance=minimum_balance,
            current_balance=current_balance,
            interest_rate=interest_rate,
            tags=tags or None
        )
        
        if account:
            print_success(f"Account created successfully! ID: {account['id']}")
    
    except ValueError:
        print_error("Invalid input.")

def list_all_accounts():
    """List all savings accounts"""
    print_header("All Savings Accounts")
    response = client.get_savings_accounts()
    if response:
        accounts = response.get("accounts", [])
        display_savings_account_table(accounts)

def list_accounts_by_user():
    """List accounts for a specific user"""
    print_header("List Accounts by User")
    
    # Show users
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
            response = client.get_savings_accounts(user_id=user_id)
            if response:
                accounts = response.get("accounts", [])
                display_savings_account_table(accounts)
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def view_account_details():
    """View account details"""
    print_header("View Account Details")
    
    response = client.get_savings_accounts()
    if not response:
        return
    
    accounts = response.get("accounts", [])
    if not accounts:
        print_error("No accounts found.")
        return
    
    display_savings_account_table(accounts)
    
    try:
        choice = int(get_input("\nSelect account (S.No)"))
        if 1 <= choice <= len(accounts):
            account_id = accounts[choice - 1]["id"]
            account = client.get_savings_account(account_id)
            if account:
                display_savings_account_details(account)
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def update_account():
    """Update account"""
    print_header("Update Account")
    
    response = client.get_savings_accounts()
    if not response:
        return
    
    accounts = response.get("accounts", [])
    if not accounts:
        print_error("No accounts found.")
        return
    
    display_savings_account_table(accounts)
    
    try:
        choice = int(get_input("\nSelect account (S.No)"))
        if 1 <= choice <= len(accounts):
            account_id = accounts[choice - 1]["id"]
            
            # Get update data
            account_name = get_input("New account name (press Enter to skip)", required=False)
            bank_name = get_input("New bank name (press Enter to skip)", required=False)
            account_type = get_input("New account type (press Enter to skip)", required=False)
            minimum_balance = get_input("New minimum balance (press Enter to skip)", required=False)
            interest_rate = get_input("New interest rate (press Enter to skip)", required=False)
            tags = get_input("New tags (press Enter to skip)", required=False)
            
            update_data = {}
            if account_name:
                update_data["account_name"] = account_name
            if bank_name:
                update_data["bank_name"] = bank_name
            if account_type:
                update_data["account_type"] = account_type
            if minimum_balance:
                update_data["minimum_balance"] = float(minimum_balance)
            if interest_rate:
                update_data["interest_rate"] = float(interest_rate)
            if tags:
                update_data["tags"] = tags
            
            if update_data:
                account = client.update_savings_account(account_id, **update_data)
                if account:
                    print_success("Account updated successfully!")
            else:
                print_error("No fields to update.")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def delete_account():
    """Delete account"""
    print_header("Delete Account")
    
    response = client.get_savings_accounts()
    if not response:
        return
    
    accounts = response.get("accounts", [])
    if not accounts:
        print_error("No accounts found.")
        return
    
    display_savings_account_table(accounts)
    
    try:
        choice = int(get_input("\nSelect account (S.No)"))
        if 1 <= choice <= len(accounts):
            account_id = accounts[choice - 1]["id"]
            confirm = get_input(f"Delete account '{accounts[choice-1]['account_name']}'? (yes/no)")
            
            if confirm.lower() in ["yes", "y"]:
                if client.delete_savings_account(account_id):
                    print_success("Account deleted successfully!")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def create_transaction():
    """Create deposit or withdrawal transaction"""
    print_header("Create Transaction")
    
    response = client.get_savings_accounts()
    if not response:
        return
    
    accounts = response.get("accounts", [])
    if not accounts:
        print_error("No accounts found.")
        return
    
    display_savings_account_table(accounts)
    
    try:
        choice = int(get_input("\nSelect account (S.No)"))
        if 1 <= choice <= len(accounts):
            account_id = accounts[choice - 1]["id"]
            
            # Get transaction details
            print("\nTransaction Types:")
            print("  1. Deposit")
            print("  2. Withdrawal")
            print("  3. Interest")
            
            txn_choice = get_input("Select transaction type (1-3)")
            
            txn_types = {"1": "deposit", "2": "withdrawal", "3": "interest"}
            if txn_choice not in txn_types:
                print_error("Invalid transaction type.")
                return
            
            amount = float(get_input("Amount"))
            description = get_input("Description (optional)", required=False)
            tags = get_input("Tags (optional)", required=False)
            transaction_date = get_datetime_input("Enter Transaction date")
            
            transaction = client.create_transaction(
                savings_account_id=account_id,
                transaction_type=txn_types[txn_choice],
                amount=amount,
                description=description or None,
                tags=tags or None,
                transaction_date=transaction_date.isoformat()
            )
            
            if transaction:
                print_success(f"Transaction created! New balance: ${float(transaction['balance_after']):,.2f}")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def view_transactions():
    """View account transactions"""
    print_header("View Transactions")
    
    response = client.get_savings_accounts()
    if not response:
        return
    
    accounts = response.get("accounts", [])
    if not accounts:
        print_error("No accounts found.")
        return
    
    display_savings_account_table(accounts)
    
    try:
        choice = int(get_input("\nSelect account (S.No)"))
        if 1 <= choice <= len(accounts):
            account_id = accounts[choice - 1]["id"]
            response = client.get_transactions(account_id)
            print("transactions response:", response)
            if response:
                transactions = response.get("transactions", [])
                display_transaction_table(transactions)
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")