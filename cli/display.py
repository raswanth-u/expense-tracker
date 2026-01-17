# cli/display.py
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import List, Dict, Any

console = Console()

def print_header(text: str):
    """Print formatted header"""
    console.print(f"\n[bold cyan]{text}[/bold cyan]")
    console.print("=" * len(text))
    
def print_success(text: str):
    """Print success message"""
    console.print(f"[green]✓[/green] {text}")
    
def print_error(text: str):
    """Print error message"""
    console.print(f"[red]✗[/red] {text}")
    
def print_info(text: str):
    """Print info message"""
    console.print(f"[blue]ℹ[/blue] {text}")
    
def display_menu(title: str, options: List[str]) -> str:
    """Display menu and get user choice"""
    print_header(title)
    for idx, option in enumerate(options, 1):
        console.print(f"  [yellow]{idx}[/yellow]. {option}")
    console.print(f"  [yellow]0[/yellow]. Back/Exit")
    return console.input("\n[bold]Choose an option: [/bold]")

def display_user_table(users: List[Dict[str, Any]]):
    """Display users in a table"""
    if not users:
        print_info("No users found.")
        return
    
    table = Table(title="Users", box=box.ROUNDED)
    table.add_column("S.No", style="cyan", justify="right")
    table.add_column("User ID", style="magenta", justify="right")
    table.add_column("Name", style="green")
    table.add_column("Email", style="blue")
    table.add_column("Status", style="yellow")
    
    for idx, user in enumerate(users, 1):
        status = "✓ Active" if user.get("is_active") else "✗ Inactive"
        table.add_row(
            str(idx),
            str(user["id"]),
            user["name"],
            user["email"],
            status
        )
    
    console.print(table)
    
def display_user_details(user: Dict[str, Any]):
    """Display detailed user information"""
    details = f"""
[cyan]User ID:[/cyan] {user['id']}
[cyan]Name:[/cyan] {user['name']}
[cyan]Email:[/cyan] {user['email']}
[cyan]Status:[/cyan] {'Active' if user.get('is_active') else 'Inactive'}
[cyan]Created At:[/cyan] {user.get('created_at', 'N/A')}
[cyan]Updated At:[/cyan] {user.get('updated_at', 'N/A')}
    """
    console.print(Panel(details, title="[bold]User Details[/bold]", border_style="green"))
    
def display_user_summary(summary: Dict[str, Any]):
    """Display user financial summary"""
    details = f"""
[cyan]User ID:[/cyan] {summary['id']}
[cyan]Name:[/cyan] {summary['name']}
[cyan]Email:[/cyan] {summary['email']}
[cyan]Status:[/cyan] {'Active' if summary.get('is_active') else 'Inactive'}

[yellow]Financial Summary:[/yellow]
  💰 Total Balance: ${summary.get('total_balance', 0):,.2f}
  🏦 Savings Accounts: {summary.get('total_savings_accounts', 0)}
  💳 Debit Cards: {summary.get('total_debit_cards', 0)}
  💳 Credit Cards: {summary.get('total_credit_cards', 0)}
  📊 Expenses: {summary.get('total_expenses', 0)}
    """
    console.print(Panel(details, title="[bold]User Summary[/bold]", border_style="cyan"))
    
def get_input(prompt: str, required: bool = True) -> str:
    """Get user input with validation"""
    while True:
        value = console.input(f"[bold]{prompt}:[/bold] ").strip()
        if value or not required:
            return value
        print_error("This field is required.")
        
def display_savings_account_table(accounts: List[Dict[str, Any]]):
    """Display savings accounts in a table"""
    if not accounts:
        print_info("No accounts found.")
        return
    
    table = Table(title="Savings Accounts", box=box.ROUNDED)
    table.add_column("S.No", style="cyan", justify="right")
    table.add_column("ID", style="magenta", justify="right")
    table.add_column("Account Name", style="green")
    table.add_column("Bank", style="blue")
    table.add_column("Account #", style="yellow")
    table.add_column("Balance", style="green", justify="right")
    
    for idx, account in enumerate(accounts, 1):
        table.add_row(
            str(idx),
            str(account["id"]),
            account["account_name"],
            account["bank_name"],
            account["account_number"],
            f"${float(account['current_balance']):,.2f}"
        )
    
    console.print(table)

def display_savings_account_details(account: Dict[str, Any]):
    """Display detailed account information"""
    details = f"""
[cyan]Account ID:[/cyan] {account['id']}
[cyan]User ID:[/cyan] {account['user_id']}
[cyan]Account Name:[/cyan] {account['account_name']}
[cyan]Bank:[/cyan] {account['bank_name']}
[cyan]Account Number:[/cyan] {account['account_number']}
[cyan]Account Type:[/cyan] {account['account_type']}
[cyan]Current Balance:[/cyan] ${float(account['current_balance']):,.2f}
[cyan]Minimum Balance:[/cyan] ${float(account['minimum_balance']):,.2f}
[cyan]Interest Rate:[/cyan] {float(account['interest_rate'])}%
[cyan]Tags:[/cyan] {account.get('tags', 'N/A')}
[cyan]Created:[/cyan] {account.get('created_at', 'N/A')}
    """
    console.print(Panel(details, title="[bold]Account Details[/bold]", border_style="green"))

def display_transaction_table(transactions: List[Dict[str, Any]]):
    """Display transactions in a table"""
    if not transactions:
        print_info("No transactions found.")
        return
    
    table = Table(title="Transactions", box=box.ROUNDED)
    table.add_column("S.No", style="cyan", justify="right")
    table.add_column("ID", style="magenta", justify="right")
    table.add_column("Type", style="yellow")
    table.add_column("Amount", style="green", justify="right")
    table.add_column("Balance After", style="blue", justify="right")
    table.add_column("Date", style="cyan")
    table.add_column("Description", style="white")
    
    for idx, txn in enumerate(transactions, 1):
        table.add_row(
            str(idx),
            str(txn["id"]),
            txn["transaction_type"],
            f"${float(txn['amount']):,.2f}",
            f"${float(txn['balance_after']):,.2f}",
            txn["transaction_date"][:10],
            txn.get("description", "")[:30] if txn.get("description") else "-"
        )
    
    console.print(table)
    
def display_debit_card_table(cards: List[Dict[str, Any]]):
    """Display debit cards in a table"""
    if not cards:
        print_info("No debit cards found.")
        return
    
    table = Table(title="Debit Cards", box=box.ROUNDED)
    table.add_column("S.No", style="cyan", justify="right")
    table.add_column("ID", style="magenta", justify="right")
    table.add_column("Card Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Last 4 Digits", style="blue")
    table.add_column("Status", style="white")
    
    for idx, card in enumerate(cards, 1):
        last_4 = card["card_number"][-4:]
        status = "✓ Active" if card.get("is_active") else "✗ Inactive"
        
        table.add_row(
            str(idx),
            str(card["id"]),
            card["card_name"],
            card["card_type"],
            f"****{last_4}",
            status
        )
    
    console.print(table)
    
def display_debit_card_details(card: Dict[str, Any]):
    """Display detailed debit card information"""
    last_4 = card["card_number"][-4:]
    status = "Active" if card.get("is_active") else "Inactive"
    expiry = card.get("expiry_date", "N/A")
    if expiry != "N/A":
        expiry = expiry[:10]
    
    details = f"""
[cyan]Card ID:[/cyan] {card['id']}
[cyan]User ID:[/cyan] {card['user_id']}
[cyan]Savings Account ID:[/cyan] {card['savings_account_id']}
[cyan]Card Name:[/cyan] {card['card_name']}
[cyan]Card Type:[/cyan] {card['card_type'].upper()}
[cyan]Card Number:[/cyan] ****{last_4}
[cyan]Expiry Date:[/cyan] {expiry}
[cyan]Status:[/cyan] {status}
[cyan]Tags:[/cyan] {card.get('tags', 'N/A')}
[cyan]Created:[/cyan] {card.get('created_at', 'N/A')[:10]}
    """
    
    # Add account details if available
    if "account_name" in card:
        details += f"""
[yellow]Linked Account:[/yellow]
[cyan]Account Name:[/cyan] {card.get('account_name', 'N/A')}
[cyan]Bank:[/cyan] {card.get('bank_name', 'N/A')}
[cyan]Balance:[/cyan] ${card.get('current_balance', 0):,.2f}
        """
    
    console.print(Panel(details, title="[bold]Debit Card Details[/bold]", border_style="green"))
    
def mask_card_number(card_number: str) -> str:
    """Mask card number showing only last 4 digits"""
    return f"****-****-****-{card_number[-4:]}"

def display_credit_card_table(cards: List[Dict[str, Any]]):
    """Display credit cards in a table"""
    if not cards:
        print_info("No credit cards found.")
        return
    
    table = Table(title="Credit Cards", box=box.ROUNDED)
    table.add_column("S.No", style="cyan", justify="right")
    table.add_column("ID", style="magenta", justify="right")
    table.add_column("Card Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Last 4", style="blue")
    table.add_column("Limit", style="cyan", justify="right")
    table.add_column("Available", style="green", justify="right")
    table.add_column("Outstanding", style="red", justify="right")
    table.add_column("Status", style="white")
    
    for idx, card in enumerate(cards, 1):
        last_4 = card["card_number"][-4:]
        status = "✓ Active" if card.get("is_active") else "✗ Inactive"
        
        table.add_row(
            str(idx),
            str(card["id"]),
            card["card_name"],
            card["card_type"].upper(),
            f"****{last_4}",
            f"${float(card['credit_limit']):,.2f}",
            f"${float(card['available_credit']):,.2f}",
            f"${float(card['outstanding_balance']):,.2f}",
            status
        )
    
    console.print(table)
    
def display_credit_card_details(card: Dict[str, Any]):
    """Display detailed credit card information"""
    last_4 = card["card_number"][-4:]
    status = "Active" if card.get("is_active") else "Inactive"
    expiry = card.get("expiry_date", "N/A")
    if expiry != "N/A" and expiry is not None:
        expiry = expiry[:10]
    
    utilization = (float(card['outstanding_balance']) / float(card['credit_limit'])) * 100
    print("EXPIRY")
    
    details = f"""
[cyan]Card ID:[/cyan] {card['id']}
[cyan]User ID:[/cyan] {card['user_id']}
[cyan]Card Name:[/cyan] {card['card_name']}
[cyan]Card Type:[/cyan] {card['card_type'].upper()}
[cyan]Card Number:[/cyan] ****{last_4}
[cyan]Expiry Date:[/cyan] {expiry}
[cyan]Status:[/cyan] {status}

[yellow]Credit Information:[/yellow]
[cyan]Credit Limit:[/cyan] ${float(card['credit_limit']):,.2f}
[cyan]Available Credit:[/cyan] ${float(card['available_credit']):,.2f}
[cyan]Outstanding Balance:[/cyan] ${float(card['outstanding_balance']):,.2f}
[cyan]Utilization:[/cyan] {utilization:.1f}%

[yellow]Billing:[/yellow]
[cyan]Billing Cycle Day:[/cyan] {card['billing_cycle_day']}
[cyan]Payment Due Day:[/cyan] {card['payment_due_day']}
[cyan]Interest Rate:[/cyan] {float(card['interest_rate'])}%
[cyan]Min Payment %:[/cyan] {float(card['minimum_payment_percentage'])}%

[cyan]Tags:[/cyan] {card.get('tags', 'N/A')}
[cyan]Created:[/cyan] {card.get('created_at', 'N/A')[:10]}
    """
    console.print(Panel(details, title="[bold]Credit Card Details[/bold]", border_style="cyan"))
    
def display_credit_transaction_table(transactions: List[Dict[str, Any]]):
    """Display credit card transactions"""
    if not transactions:
        print_info("No transactions found.")
        return
    
    table = Table(title="Credit Card Transactions", box=box.ROUNDED)
    table.add_column("S.No", style="cyan", justify="right")
    table.add_column("ID", style="magenta", justify="right")
    table.add_column("Type", style="yellow")
    table.add_column("Amount", style="green", justify="right")
    table.add_column("Outstanding After", style="red", justify="right")
    table.add_column("Date", style="cyan")
    table.add_column("Merchant", style="blue")
    
    for idx, txn in enumerate(transactions, 1):
        amount_str = f"${float(txn['amount']):,.2f}"
        if float(txn['amount']) < 0:
            amount_str = f"-${abs(float(txn['amount'])):,.2f}"
        
        table.add_row(
            str(idx),
            str(txn["id"]),
            txn["transaction_type"].replace("_", " ").title(),
            amount_str,
            f"${float(txn['outstanding_after']):,.2f}",
            txn["transaction_date"][:10],
            txn.get("merchant_name", "N/A")[:20]
        )
    
    console.print(table)
    
def display_credit_payment_table(payments: List[Dict[str, Any]]):
    """Display credit card payments"""
    if not payments:
        print_info("No payments found.")
        return
    
    table = Table(title="Credit Card Payments", box=box.ROUNDED)
    table.add_column("S.No", style="cyan", justify="right")
    table.add_column("ID", style="magenta", justify="right")
    table.add_column("Amount", style="green", justify="right")
    table.add_column("Outstanding Before", style="red", justify="right")
    table.add_column("Outstanding After", style="yellow", justify="right")
    table.add_column("Date", style="cyan")
    table.add_column("Method", style="blue")
    
    for idx, payment in enumerate(payments, 1):
        table.add_row(
            str(idx),
            str(payment["id"]),
            f"${float(payment['payment_amount']):,.2f}",
            f"${float(payment['outstanding_before']):,.2f}",
            f"${float(payment['outstanding_after']):,.2f}",
            payment["payment_date"][:10],
            payment["payment_method"].replace("_", " ").title()
        )
    
    console.print(table)
    
def display_expense_table(expenses: List[Dict[str, Any]]):
    """Display expenses in a table"""
    if not expenses:
        print_info("No expenses found.")
        return
    
    table = Table(title="Expenses", box=box.ROUNDED)
    table.add_column("S.No", style="cyan", justify="right")
    table.add_column("ID", style="magenta", justify="right")
    table.add_column("Date", style="blue")
    table.add_column("Category", style="yellow")
    table.add_column("Amount", style="green", justify="right")
    table.add_column("Method", style="cyan")
    table.add_column("Merchant", style="white")
    table.add_column("Description", style="orange1")
    
    for idx, expense in enumerate(expenses, 1):
        date_str = expense["expense_date"][:10]
        category = expense["category"].replace("_", " ").title()
        method = expense["payment_method"].replace("_", " ").title()
        merchant = (expense.get("merchant_name") or "N/A")[:20]
        description = (expense.get("description") or "N/A")[:30]
        
        table.add_row(
            str(idx),
            str(expense["id"]),
            date_str,
            category,
            f"${float(expense['amount']):,.2f}",
            method,
            merchant,
            description
        )
    
    console.print(table)
    
def display_expense_details(expense: Dict[str, Any]):
    """Display detailed expense information"""
    details = f"""
[cyan]Expense ID:[/cyan] {expense['id']}
[cyan]User ID:[/cyan] {expense['user_id']}
[cyan]Category:[/cyan] {expense['category'].replace('_', ' ').title()}
[cyan]Amount:[/cyan] ${float(expense['amount']):,.2f}
[cyan]Payment Method:[/cyan] {expense['payment_method'].replace('_', ' ').title()}
[cyan]Date:[/cyan] {expense['expense_date'][:10]}
[cyan]Merchant:[/cyan] {expense.get('merchant_name', 'N/A')}
[cyan]Description:[/cyan] {expense.get('description', 'N/A')}
[cyan]Tags:[/cyan] {expense.get('tags', 'N/A')}
    """
    
    # Add card/account info if available
    if "card_name" in expense:
        details += f"\n[yellow]Payment Details:[/yellow]\n"
        details += f"[cyan]Card:[/cyan] {expense.get('card_name', 'N/A')}\n"
        if "account_name" in expense:
            details += f"[cyan]Account:[/cyan] {expense.get('account_name', 'N/A')}\n"
            details += f"[cyan]Bank:[/cyan] {expense.get('bank_name', 'N/A')}\n"
    
    console.print(Panel(details, title="[bold]Expense Details[/bold]", border_style="green"))
    
def display_expense_statistics(stats: Dict[str, Any]):
    """Display expense statistics"""
    if stats['total_expenses'] == 0:
        print_info("No expenses found for the selected period.")
        return
    
    # Summary
    summary = f"""
[yellow]Summary:[/yellow]
[cyan]Total Expenses:[/cyan] {stats['total_expenses']}
[cyan]Total Amount:[/cyan] ${float(stats['total_amount']):,.2f}
[cyan]Average Expense:[/cyan] ${float(stats['average_expense']):,.2f}
    """
    
    if 'date_range' in stats and stats['date_range']:
        date_range = stats['date_range']
        summary += f"[cyan]Date Range:[/cyan] {date_range.get('start', 'N/A')[:10]} to {date_range.get('end', 'N/A')[:10]}\n"
    
    console.print(Panel(summary, title="[bold]Expense Statistics[/bold]", border_style="cyan"))
    
    # By Category
    if stats['by_category']:
        print("by category")
        console.print("\n[yellow]By Category:[/yellow]")
        cat_table = Table(box=box.SIMPLE)
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Amount", style="green", justify="right")
        cat_table.add_column("Percentage", style="yellow", justify="right")
        
        total = float(stats['total_amount'])
        for category, amount in sorted(
            stats['by_category'].items(),
            key=lambda x: float(x[1]),
            reverse=True
        ):
            amount_float = float(amount)
            percentage = (amount_float / total) * 100
            cat_table.add_row(
                category.replace('_', ' ').title(),
                f"${amount_float:,.2f}",
                f"{percentage:.1f}%"
            )
        
        console.print(cat_table)
    
    # By Payment Method
    if stats['by_payment_method']:
        console.print("\n[yellow]By Payment Method:[/yellow]")
        method_table = Table(box=box.SIMPLE)
        method_table.add_column("Method", style="cyan")
        method_table.add_column("Amount", style="green", justify="right")
        method_table.add_column("Percentage", style="yellow", justify="right")
        
        total = float(stats['total_amount'])
        for method, amount in sorted(
            stats['by_payment_method'].items(),
            key=lambda x: float(x[1]),
            reverse=True
        ):
            amount_float = float(amount)
            percentage = (amount_float / total) * 100
            method_table.add_row(
                method.replace('_', ' ').title(),
                f"${amount_float:,.2f}",
                f"{percentage:.1f}%"
            )
        
        console.print(method_table)
        
def display_monthly_summary(summary: Dict[str, Any]):
    """Display monthly expense summary"""
    details = f"""
[yellow]Period:[/yellow] {summary['period']}
[cyan]Total Expenses:[/cyan] {summary['expense_count']}
[cyan]Total Amount:[/cyan] ${float(summary['total_amount']):,.2f}
[cyan]Top Category:[/cyan] {summary.get('top_category', 'N/A').replace('_', ' ').title()}
[cyan]Top Merchant:[/cyan] {summary.get('top_merchant', 'N/A')}
    """
    
    console.print(Panel(details, title="[bold]Monthly Summary[/bold]", border_style="yellow"))