# cli/menus/debit_card_menu.py
from cli.client import client
from cli.display import (
    display_menu, display_debit_card_table, display_debit_card_details,
    display_user_table, display_savings_account_table, get_input,
    print_success, print_error, print_header, mask_card_number
)
from datetime import datetime

def debit_card_menu():
    """Debit card management menu"""
    while True:
        choice = display_menu(
            "Debit Card Management",
            [
                "Create Debit Card",
                "List All Cards",
                "List Cards by User",
                "View Card Details",
                "Update Card",
                "Activate/Deactivate Card",
                "Delete Card"
            ]
        )
        
        if choice == "0":
            break
        elif choice == "1":
            create_card()
        elif choice == "2":
            list_all_cards()
        elif choice == "3":
            list_cards_by_user()
        elif choice == "4":
            view_card_details()
        elif choice == "5":
            update_card()
        elif choice == "6":
            toggle_card_status()
        elif choice == "7":
            delete_card()
        else:
            print_error("Invalid option. Please try again.")

def create_card():
    """Create a new debit card"""
    print_header("Create Debit Card")
    
    # Show users
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
        
        # Show user's savings accounts
        accounts_response = client.get_savings_accounts(user_id=user_id)
        if not accounts_response:
            return
        
        accounts = accounts_response.get("accounts", [])
        if not accounts:
            print_error("User has no savings accounts. Create one first.")
            return
        
        display_savings_account_table(accounts)
        
        account_choice = int(get_input("\nSelect savings account (S.No)"))
        if not (1 <= account_choice <= len(accounts)):
            print_error("Invalid selection.")
            return
        
        account_id = accounts[account_choice - 1]["id"]
        
        # Get card details
        card_name = get_input("Card name (e.g., 'Primary Debit Card')")
        card_number = get_input("Card number (13-19 digits)")
        
        print("\nCard Types:")
        print("  1. Visa")
        print("  2. Mastercard")
        print("  3. RuPay")
        
        card_type_choice = get_input("Select card type (1-3)")
        card_types = {"1": "visa", "2": "mastercard", "3": "rupay"}
        
        if card_type_choice not in card_types:
            print_error("Invalid card type.")
            return
        
        expiry_date_str = get_input("Expiry date (YYYY-MM-DD, optional)", required=False)
        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").isoformat()
            except ValueError:
                print_error("Invalid date format.")
                return
        
        is_active_input = get_input("Active status (yes/no, default: yes)", required=False)
        is_active = is_active_input.lower() not in ["no", "n"] if is_active_input else True
        
        tags = get_input("Tags (optional)", required=False)
        
        card = client.create_debit_card(
            user_id=user_id,
            savings_account_id=account_id,
            card_name=card_name,
            card_number=card_number,
            card_type=card_types[card_type_choice],
            expiry_date=expiry_date,
            is_active=is_active,
            tags=tags or None
        )
        
        if card:
            print_success(f"Debit card created successfully! ID: {card['id']}")
    
    except ValueError:
        print_error("Invalid input.")

def list_all_cards():
    """List all debit cards"""
    print_header("All Debit Cards")
    response = client.get_debit_cards()
    if response:
        cards = response.get("cards", [])
        display_debit_card_table(cards)
        input("\nPress Enter to continue...")

def list_cards_by_user():
    """List cards for a specific user"""
    print_header("List Cards by User")
    
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
            response = client.get_debit_cards(user_id=user_id)
            if response:
                cards = response.get("cards", [])
                display_debit_card_table(cards)
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def view_card_details():
    """View card details"""
    print_header("View Card Details")
    
    response = client.get_debit_cards()
    if not response:
        return
    
    cards = response.get("cards", [])
    if not cards:
        print_error("No cards found.")
        return
    
    display_debit_card_table(cards)
    
    try:
        choice = int(get_input("\nSelect card (S.No)"))
        if 1 <= choice <= len(cards):
            card_id = cards[choice - 1]["id"]
            
            # Get detailed view with account info
            card = client.get_debit_card_details(card_id)
            if card:
                display_debit_card_details(card)
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def update_card():
    """Update card details"""
    print_header("Update Card")
    
    response = client.get_debit_cards()
    if not response:
        return
    
    cards = response.get("cards", [])
    if not cards:
        print_error("No cards found.")
        return
    
    display_debit_card_table(cards)
    
    try:
        choice = int(get_input("\nSelect card (S.No)"))
        if 1 <= choice <= len(cards):
            card_id = cards[choice - 1]["id"]
            
            # Get update data
            card_name = get_input("New card name (press Enter to skip)", required=False)
            expiry_date_str = get_input("New expiry date YYYY-MM-DD (press Enter to skip)", required=False)
            is_active = get_input("Active status yes/no (press Enter to skip)", required=False)
            tags = get_input("New tags (press Enter to skip)", required=False)
            
            update_data = {}
            
            if card_name:
                update_data["card_name"] = card_name
            
            if expiry_date_str:
                try:
                    update_data["expiry_date"] = datetime.strptime(
                        expiry_date_str, 
                        "%Y-%m-%d"
                    ).isoformat()
                except ValueError:
                    print_error("Invalid date format.")
                    return
            
            if is_active:
                update_data["is_active"] = is_active.lower() in ["yes", "y"]
            
            if tags:
                update_data["tags"] = tags
            
            if update_data:
                card = client.update_debit_card(card_id, **update_data)
                if card:
                    print_success("Card updated successfully!")
            else:
                print_error("No fields to update.")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def toggle_card_status():
    """Activate or deactivate a card"""
    print_header("Activate/Deactivate Card")
    
    response = client.get_debit_cards()
    if not response:
        return
    
    cards = response.get("cards", [])
    if not cards:
        print_error("No cards found.")
        return
    
    display_debit_card_table(cards)
    
    try:
        choice = int(get_input("\nSelect card (S.No)"))
        if 1 <= choice <= len(cards):
            card_id = cards[choice - 1]["id"]
            current_status = cards[choice - 1]["is_active"]
            
            action = "deactivate" if current_status else "activate"
            confirm = get_input(f"Do you want to {action} this card? (yes/no)")
            
            if confirm.lower() in ["yes", "y"]:
                if current_status:
                    card = client.deactivate_debit_card(card_id)
                else:
                    card = client.activate_debit_card(card_id)
                
                if card:
                    print_success(f"Card {action}d successfully!")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def delete_card():
    """Delete a card"""
    print_header("Delete Card")
    
    response = client.get_debit_cards()
    if not response:
        return
    
    cards = response.get("cards", [])
    if not cards:
        print_error("No cards found.")
        return
    
    display_debit_card_table(cards)
    
    try:
        choice = int(get_input("\nSelect card (S.No)"))
        if 1 <= choice <= len(cards):
            card_id = cards[choice - 1]["id"]
            confirm = get_input(f"Delete card '{cards[choice-1]['card_name']}'? (yes/no)")
            
            if confirm.lower() in ["yes", "y"]:
                if client.delete_debit_card(card_id):
                    print_success("Card deleted successfully!")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")