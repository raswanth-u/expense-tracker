# cli/menus/credit_card_menu.py
from cli.client import client
from cli.display import (
    display_menu, display_credit_card_table, display_credit_card_details,
    display_credit_transaction_table, display_credit_payment_table,
    display_user_table, display_savings_account_table, get_input,
    print_success, print_error, print_header, console
)
from cli.config import setup_cli_logging
from datetime import datetime
from decimal import Decimal

logger = setup_cli_logging()

def credit_card_menu():
    """Credit card management menu"""
    logger.info("Entered credit card menu")
    
    while True:
        choice = display_menu(
            "Credit Card Management",
            [
                "Create Credit Card",
                "List All Cards",
                "List Cards by User",
                "View Card Details",
                "Update Card",
                "Delete Card",
                "Create Transaction (Purchase/Refund/Fee)",
                "View Transactions",
                "Make Payment",
                "View Payments"
            ]
        )
        
        if choice == "0":
            logger.info("Exiting credit card menu")
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
            delete_card()
        elif choice == "7":
            create_transaction()
        elif choice == "8":
            view_transactions()
        elif choice == "9":
            make_payment()
        elif choice == "10":
            view_payments()
        else:
            print_error("Invalid option. Please try again.")

def create_card():
    """Create a new credit card"""
    print_header("Create Credit Card")
    logger.info("Creating new credit card")
    
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
        logger.debug(f"Selected user_id: {user_id}")
        
        # Get card details
        console.print("\n[bold cyan]Card Information[/bold cyan]")
        card_name = get_input("Card name (e.g., 'HDFC Regalia')")
        card_number = get_input("Card number (13-19 digits)")
        
        # Validate card number
        if not card_number.isdigit() or not (13 <= len(card_number) <= 19):
            print_error("Invalid card number. Must be 13-19 digits.")
            return
        
        # Card type
        console.print("\n[yellow]Card Types:[/yellow]")
        console.print("  1. Visa")
        console.print("  2. Mastercard")
        console.print("  3. RuPay")
        console.print("  4. American Express (AMEX)")
        
        card_type_choice = get_input("Select card type (1-4)")
        card_types = {
            "1": "visa",
            "2": "mastercard",
            "3": "rupay",
            "4": "amex"
        }
        
        if card_type_choice not in card_types:
            print_error("Invalid card type.")
            return
        
        # Credit limit and billing info
        console.print("\n[bold cyan]Credit & Billing Information[/bold cyan]")
        credit_limit = float(get_input("Credit limit ($)"))
        
        if credit_limit <= 0:
            print_error("Credit limit must be positive.")
            return
        
        billing_cycle_day = int(get_input("Billing cycle day (1-31)"))
        if not (1 <= billing_cycle_day <= 31):
            print_error("Billing cycle day must be between 1 and 31.")
            return
        
        payment_due_day = int(get_input("Payment due day (1-31)"))
        if not (1 <= payment_due_day <= 31):
            print_error("Payment due day must be between 1 and 31.")
            return
        
        if payment_due_day <= billing_cycle_day:
            print_error("Payment due day must be after billing cycle day.")
            return
        
        interest_rate = float(get_input("Interest rate % (default: 0)", required=False) or "0")
        minimum_payment_percentage = float(
            get_input("Minimum payment % (default: 5)", required=False) or "5"
        )
        
        # Optional fields
        console.print("\n[bold cyan]Optional Information[/bold cyan]")
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
        
        # Create card
        card = client.create_credit_card(
            user_id=user_id,
            card_name=card_name,
            card_number=card_number,
            card_type=card_types[card_type_choice],
            credit_limit=credit_limit,
            billing_cycle_day=billing_cycle_day,
            payment_due_day=payment_due_day,
            interest_rate=interest_rate,
            minimum_payment_percentage=minimum_payment_percentage,
            expiry_date=expiry_date,
            is_active=is_active,
            tags=tags or None
        )
        
        if card:
            logger.info(f"Credit card created: ID={card['id']}")
            print_success(f"Credit card created successfully! ID: {card['id']}")
            console.print(f"[green]Credit Limit:[/green] ${float(card['credit_limit']):,.2f}")
            console.print(f"[green]Available Credit:[/green] ${float(card['available_credit']):,.2f}")
    
    except ValueError as e:
        logger.error(f"Validation error in create_card: {str(e)}")
        print_error(f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error in create_card: {str(e)}", exc_info=True)
        print_error(f"An error occurred: {str(e)}")

def list_all_cards():
    """List all credit cards"""
    print_header("All Credit Cards")
    logger.debug("Listing all credit cards")
    
    response = client.get_credit_cards()
    if response:
        cards = response.get("cards", [])
        display_credit_card_table(cards)
        
        if cards:
            console.print(f"\n[cyan]Total cards:[/cyan] {len(cards)}")
            total_limit = sum(float(card['credit_limit']) for card in cards)
            total_outstanding = sum(float(card['outstanding_balance']) for card in cards)
            console.print(f"[cyan]Total Credit Limit:[/cyan] ${total_limit:,.2f}")
            console.print(f"[cyan]Total Outstanding:[/cyan] ${total_outstanding:,.2f}")
        
        input("\nPress Enter to continue...")

def list_cards_by_user():
    """List cards for a specific user"""
    print_header("List Cards by User")
    logger.debug("Listing cards by user")
    
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
            logger.debug(f"Fetching cards for user_id: {user_id}")
            
            response = client.get_credit_cards(user_id=user_id)
            if response:
                cards = response.get("cards", [])
                display_credit_card_table(cards)
                
                if cards:
                    console.print(f"\n[cyan]Total cards:[/cyan] {len(cards)}")
                
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def view_card_details():
    """View detailed card information"""
    print_header("View Card Details")
    logger.debug("Viewing card details")
    
    response = client.get_credit_cards()
    if not response:
        return
    
    cards = response.get("cards", [])
    if not cards:
        print_error("No cards found.")
        return
    
    display_credit_card_table(cards)
    
    try:
        choice = int(get_input("\nSelect card (S.No)"))
        if 1 <= choice <= len(cards):
            card_id = cards[choice - 1]["id"]
            logger.debug(f"Fetching details for card_id: {card_id}")
            
            card = client.get_credit_card(card_id)
            if card:
                display_credit_card_details(card)
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def update_card():
    """Update card details"""
    print_header("Update Card")
    logger.info("Updating card")
    
    response = client.get_credit_cards()
    if not response:
        return
    
    cards = response.get("cards", [])
    if not cards:
        print_error("No cards found.")
        return
    
    display_credit_card_table(cards)
    
    try:
        choice = int(get_input("\nSelect card (S.No)"))
        if 1 <= choice <= len(cards):
            card_id = cards[choice - 1]["id"]
            
            console.print("\n[yellow]Leave fields empty to keep current value[/yellow]")
            
            # Get update data
            card_name = get_input("New card name (press Enter to skip)", required=False)
            credit_limit = get_input("New credit limit (press Enter to skip)", required=False)
            interest_rate = get_input("New interest rate (press Enter to skip)", required=False)
            min_payment = get_input("New minimum payment % (press Enter to skip)", required=False)
            expiry_date_str = get_input("New expiry date YYYY-MM-DD (press Enter to skip)", required=False)
            is_active = get_input("Active status yes/no (press Enter to skip)", required=False)
            tags = get_input("New tags (press Enter to skip)", required=False)
            
            update_data = {}
            
            if card_name:
                update_data["card_name"] = card_name
            
            if credit_limit:
                try:
                    update_data["credit_limit"] = float(credit_limit)
                except ValueError:
                    print_error("Invalid credit limit.")
                    return
            
            if interest_rate:
                try:
                    update_data["interest_rate"] = float(interest_rate)
                except ValueError:
                    print_error("Invalid interest rate.")
                    return
            
            if min_payment:
                try:
                    update_data["minimum_payment_percentage"] = float(min_payment)
                except ValueError:
                    print_error("Invalid minimum payment percentage.")
                    return
            
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
                logger.info(f"Updating card {card_id} with data: {update_data}")
                card = client.update_credit_card(card_id, **update_data)
                if card:
                    print_success("Card updated successfully!")
                    display_credit_card_details(card)
                    input("\nPress Enter to continue...")
            else:
                print_error("No fields to update.")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")
    except Exception as e:
        logger.error(f"Error in update_card: {str(e)}", exc_info=True)
        print_error(f"An error occurred: {str(e)}")

def delete_card():
    """Delete a credit card"""
    print_header("Delete Card")
    logger.warning("Attempting to delete card")
    
    response = client.get_credit_cards()
    if not response:
        return
    
    cards = response.get("cards", [])
    if not cards:
        print_error("No cards found.")
        return
    
    display_credit_card_table(cards)
    
    try:
        choice = int(get_input("\nSelect card (S.No)"))
        if 1 <= choice <= len(cards):
            card_id = cards[choice - 1]["id"]
            card_name = cards[choice - 1]['card_name']
            outstanding = float(cards[choice - 1]['outstanding_balance'])
            
            if outstanding > 0:
                console.print(
                    f"\n[yellow]⚠ Warning: This card has an outstanding balance of ${outstanding:,.2f}[/yellow]"
                )
            
            confirm = get_input(f"Delete card '{card_name}'? This will delete all transactions and payments. (yes/no)")
            
            if confirm.lower() in ["yes", "y"]:
                logger.warning(f"Deleting card {card_id}")
                if client.delete_credit_card(card_id):
                    print_success("Card deleted successfully!")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")
    except Exception as e:
        logger.error(f"Error in delete_card: {str(e)}", exc_info=True)
        print_error(f"An error occurred: {str(e)}")

def create_transaction():
    """Create a credit card transaction"""
    print_header("Create Transaction")
    logger.info("Creating credit card transaction")
    
    response = client.get_credit_cards()
    if not response:
        return
    
    cards = response.get("cards", [])
    if not cards:
        print_error("No cards found.")
        return
    
    display_credit_card_table(cards)
    
    try:
        choice = int(get_input("\nSelect card (S.No)"))
        if 1 <= choice <= len(cards):
            card_id = cards[choice - 1]["id"]
            available = float(cards[choice - 1]['available_credit'])
            
            console.print(f"\n[cyan]Available Credit:[/cyan] ${available:,.2f}")
            
            # Transaction type
            console.print("\n[yellow]Transaction Types:[/yellow]")
            console.print("  1. Purchase")
            console.print("  2. Refund")
            console.print("  3. Interest Charge")
            console.print("  4. Late Fee")
            console.print("  5. Annual Fee")
            
            txn_choice = get_input("Select transaction type (1-5)")
            txn_types = {
                "1": "purchase",
                "2": "refund",
                "3": "interest_charge",
                "4": "late_fee",
                "5": "annual_fee"
            }
            
            if txn_choice not in txn_types:
                print_error("Invalid transaction type.")
                return
            
            txn_type = txn_types[txn_choice]
            
            # Amount
            amount = float(get_input("Amount ($)"))
            
            if amount <= 0:
                print_error("Amount must be positive.")
                return
            
            # For refunds, amount will be converted to negative by the API
            if txn_type == "purchase" and amount > available:
                console.print(
                    f"\n[red]⚠ Warning: This transaction exceeds available credit by ${amount - available:,.2f}[/red]"
                )
                confirm = get_input("Continue anyway? (yes/no)")
                if confirm.lower() not in ["yes", "y"]:
                    return
            
            # Optional fields
            description = get_input("Description (optional)", required=False)
            merchant_name = get_input("Merchant name (optional)", required=False)
            tags = get_input("Tags (optional)", required=False)
            
            # Create transaction
            logger.info(f"Creating {txn_type} transaction for card {card_id}, amount: ${amount}")
            
            transaction = client.create_credit_transaction(
                credit_card_id=card_id,
                transaction_type=txn_type,
                amount=amount,
                description=description or None,
                merchant_name=merchant_name or None,
                tags=tags or None
            )
            
            if transaction:
                logger.info(f"Transaction created: ID={transaction['id']}")
                print_success("Transaction created successfully!")
                console.print(f"\n[cyan]Transaction ID:[/cyan] {transaction['id']}")
                console.print(f"[cyan]Amount:[/cyan] ${float(transaction['amount']):,.2f}")
                console.print(f"[cyan]Outstanding After:[/cyan] ${float(transaction['outstanding_after']):,.2f}")
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError as e:
        logger.error(f"Validation error in create_transaction: {str(e)}")
        print_error(f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error in create_transaction: {str(e)}", exc_info=True)
        print_error(f"An error occurred: {str(e)}")

def view_transactions():
    """View credit card transactions"""
    print_header("View Transactions")
    logger.debug("Viewing transactions")
    
    response = client.get_credit_cards()
    if not response:
        return
    
    cards = response.get("cards", [])
    if not cards:
        print_error("No cards found.")
        return
    
    display_credit_card_table(cards)
    
    try:
        choice = int(get_input("\nSelect card (S.No)"))
        if 1 <= choice <= len(cards):
            card_id = cards[choice - 1]["id"]
            logger.debug(f"Fetching transactions for card_id: {card_id}")
            
            response = client.get_credit_transactions(card_id)
            if response:
                transactions = response.get("transactions", [])
                display_credit_transaction_table(transactions)
                
                if transactions:
                    console.print(f"\n[cyan]Total transactions:[/cyan] {len(transactions)}")
                    total_purchases = sum(
                        float(t['amount']) for t in transactions
                        if t['transaction_type'] == 'purchase'
                    )
                    total_refunds = sum(
                        abs(float(t['amount'])) for t in transactions
                        if t['transaction_type'] == 'refund'
                    )
                    console.print(f"[cyan]Total Purchases:[/cyan] ${total_purchases:,.2f}")
                    console.print(f"[cyan]Total Refunds:[/cyan] ${total_refunds:,.2f}")
                
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")

def make_payment():
    """Make a payment from savings account to credit card"""
    print_header("Make Payment")
    logger.info("Processing credit card payment")
    
    # Show credit cards
    response = client.get_credit_cards()
    if not response:
        return
    
    cards = response.get("cards", [])
    if not cards:
        print_error("No cards found.")
        return
    
    display_credit_card_table(cards)
    
    try:
        card_choice = int(get_input("\nSelect card (S.No)"))
        if not (1 <= card_choice <= len(cards)):
            print_error("Invalid selection.")
            return
        
        card_id = cards[card_choice - 1]["id"]
        outstanding = float(cards[card_choice - 1]['outstanding_balance'])
        
        if outstanding == 0:
            print_error("No outstanding balance on this card.")
            return
        
        console.print(f"\n[cyan]Outstanding Balance:[/cyan] ${outstanding:,.2f}")
        
        # Show savings accounts
        console.print("\n[bold cyan]Select Savings Account for Payment[/bold cyan]")
        accounts_response = client.get_savings_accounts()
        if not accounts_response:
            return
        
        accounts = accounts_response.get("accounts", [])
        if not accounts:
            print_error("No savings accounts found.")
            return
        
        display_savings_account_table(accounts)
        
        account_choice = int(get_input("\nSelect savings account (S.No)"))
        if not (1 <= account_choice <= len(accounts)):
            print_error("Invalid selection.")
            return
        
        account_id = accounts[account_choice - 1]["id"]
        account_balance = float(accounts[account_choice - 1]['current_balance'])
        
        console.print(f"\n[cyan]Account Balance:[/cyan] ${account_balance:,.2f}")
        
        # Payment amount
        payment_amount = float(get_input(f"Payment amount (max: ${min(outstanding, account_balance):,.2f})"))
        
        if payment_amount <= 0:
            print_error("Payment amount must be positive.")
            return
        
        if payment_amount > outstanding:
            print_error(f"Payment cannot exceed outstanding balance of ${outstanding:,.2f}")
            return
        
        if payment_amount > account_balance:
            print_error(f"Insufficient account balance. Available: ${account_balance:,.2f}")
            return
        
        # Payment method
        console.print("\n[yellow]Payment Methods:[/yellow]")
        console.print("  1. Auto Debit")
        console.print("  2. Manual")
        console.print("  3. Net Banking")
        
        method_choice = get_input("Select payment method (1-3)")
        payment_methods = {
            "1": "auto_debit",
            "2": "manual",
            "3": "net_banking"
        }
        
        if method_choice not in payment_methods:
            print_error("Invalid payment method.")
            return
        
        description = get_input("Description (optional)", required=False)
        
        # Confirm payment
        console.print("\n[yellow]Payment Summary:[/yellow]")
        console.print(f"[cyan]Card:[/cyan] {cards[card_choice - 1]['card_name']}")
        console.print(f"[cyan]Account:[/cyan] {accounts[account_choice - 1]['account_name']}")
        console.print(f"[cyan]Amount:[/cyan] ${payment_amount:,.2f}")
        console.print(f"[cyan]Method:[/cyan] {payment_methods[method_choice].replace('_', ' ').title()}")
        
        confirm = get_input("\nConfirm payment? (yes/no)")
        
        if confirm.lower() in ["yes", "y"]:
            logger.info(
                f"Processing payment: card_id={card_id}, "
                f"account_id={account_id}, amount=${payment_amount}"
            )
            
            payment = client.create_credit_payment(
                credit_card_id=card_id,
                savings_account_id=account_id,
                payment_amount=payment_amount,
                payment_method=payment_methods[method_choice],
                description=description or None
            )
            
            if payment:
                logger.info(f"Payment processed: ID={payment['id']}")
                print_success("Payment processed successfully!")
                console.print(f"\n[cyan]Payment ID:[/cyan] {payment['id']}")
                console.print(f"[cyan]Amount:[/cyan] ${float(payment['payment_amount']):,.2f}")
                console.print(f"[cyan]Outstanding Before:[/cyan] ${float(payment['outstanding_before']):,.2f}")
                console.print(f"[cyan]Outstanding After:[/cyan] ${float(payment['outstanding_after']):,.2f}")
                input("\nPress Enter to continue...")
    
    except ValueError as e:
        logger.error(f"Validation error in make_payment: {str(e)}")
        print_error(f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error in make_payment: {str(e)}", exc_info=True)
        print_error(f"An error occurred: {str(e)}")

def view_payments():
    """View credit card payment history"""
    print_header("View Payments")
    logger.debug("Viewing payment history")
    
    response = client.get_credit_cards()
    if not response:
        return
    
    cards = response.get("cards", [])
    if not cards:
        print_error("No cards found.")
        return
    
    display_credit_card_table(cards)
    
    try:
        choice = int(get_input("\nSelect card (S.No)"))
        if 1 <= choice <= len(cards):
            card_id = cards[choice - 1]["id"]
            logger.debug(f"Fetching payments for card_id: {card_id}")
            
            response = client.get_credit_payments(card_id)
            if response:
                payments = response.get("payments", [])
                display_credit_payment_table(payments)
                
                if payments:
                    console.print(f"\n[cyan]Total payments:[/cyan] {len(payments)}")
                    total_paid = sum(float(p['payment_amount']) for p in payments)
                    console.print(f"[cyan]Total Amount Paid:[/cyan] ${total_paid:,.2f}")
                
                input("\nPress Enter to continue...")
        else:
            print_error("Invalid selection.")
    except ValueError:
        print_error("Invalid input.")