# scripts/complete_test.py
"""
Complete end-to-end test for expense tracker
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "your-secret-api-key"
HEADERS = {"X-API-Key": API_KEY}

def test_complete_flow():
    """Test complete expense tracking flow"""
    
    print("🚀 Starting complete test flow...\n")
    
    # 1. Create User
    print("1️⃣ Creating user...")
    user = requests.post(
        f"{BASE_URL}/users/",
        json={"name": "Test User", "email": "test@example.com"},
        headers=HEADERS
    ).json()
    print(f"   ✅ User: {user['name']} (ID: {user['id']})\n")
    
    # 2. Create Savings Account
    print("2️⃣ Creating savings account...")
    account = requests.post(
        f"{BASE_URL}/savings-accounts/",
        json={
            "user_id": user['id'],
            "account_name": "Main Account",
            "bank_name": "Test Bank",
            "account_number": "ACC123456",
            "account_type": "savings",
            "current_balance": 100000.00,
            "minimum_balance": 5000.00
        },
        headers=HEADERS
    ).json()
    print(f"   ✅ Account: {account['account_name']} (Balance: ${account['current_balance']})\n")
    
    # 3. Create Debit Card
    print("3️⃣ Creating debit card...")
    debit_card = requests.post(
        f"{BASE_URL}/debit-cards/",
        json={
            "user_id": user['id'],
            "savings_account_id": account['id'],
            "card_name": "Main Debit Card",
            "card_number": "4111111111111111",
            "card_type": "visa"
        },
        headers=HEADERS
    ).json()
    print(f"   ✅ Debit Card: {debit_card['card_name']}\n")
    
    # 4. Create Credit Card
    print("4️⃣ Creating credit card...")
    credit_card = requests.post(
        f"{BASE_URL}/credit-cards/",
        json={
            "user_id": user['id'],
            "card_name": "Platinum Card",
            "card_number": "5555555555554444",
            "card_type": "mastercard",
            "credit_limit": 200000.00,
            "billing_cycle_day": 1,
            "payment_due_day": 20
        },
        headers=HEADERS
    ).json()
    print(f"   ✅ Credit Card: {credit_card['card_name']} (Limit: ${credit_card['credit_limit']})\n")
    
    # 5. Create Expenses
    print("5️⃣ Creating expenses...\n")
    
    # Debit card expense
    print("   📝 Debit card expense (Groceries)...")
    expense1 = requests.post(
        f"{BASE_URL}/expenses/",
        json={
            "user_id": user['id'],
            "debit_card_id": debit_card['id'],
            "category": "groceries",
            "amount": 5000.00,
            "payment_method": "debit_card",
            "merchant_name": "Supermart",
            "description": "Weekly groceries"
        },
        headers=HEADERS
    ).json()
    print(f"   ✅ Expense created: ${expense1['amount']}")
    
    # Credit card expense
    print("   📝 Credit card expense (Shopping)...")
    expense2 = requests.post(
        f"{BASE_URL}/expenses/",
        json={
            "user_id": user['id'],
            "credit_card_id": credit_card['id'],
            "category": "shopping",
            "amount": 25000.00,
            "payment_method": "credit_card",
            "merchant_name": "Amazon",
            "description": "Electronics"
        },
        headers=HEADERS
    ).json()
    print(f"   ✅ Expense created: ${expense2['amount']}")
    
    # Cash expense
    print("   📝 Cash expense (Food)...")
    expense3 = requests.post(
        f"{BASE_URL}/expenses/",
        json={
            "user_id": user['id'],
            "category": "food",
            "amount": 1500.00,
            "payment_method": "cash",
            "merchant_name": "Restaurant",
            "description": "Dinner"
        },
        headers=HEADERS
    ).json()
    print(f"   ✅ Expense created: ${expense3['amount']}\n")
    
    # 6. Make Credit Card Payment
    print("6️⃣ Making credit card payment...")
    payment = requests.post(
        f"{BASE_URL}/credit-cards/payments",
        json={
            "credit_card_id": credit_card['id'],
            "savings_account_id": account['id'],
            "payment_amount": 10000.00,
            "payment_method": "net_banking"
        },
        headers=HEADERS
    ).json()
    print(f"   ✅ Payment: ${payment['payment_amount']}\n")
    
    # 7. Get Statistics
    print("7️⃣ Getting expense statistics...")
    stats = requests.get(
        f"{BASE_URL}/expenses/statistics/user/{user['id']}",
        headers=HEADERS
    ).json()
    
    print("\n" + "="*60)
    print("📊 EXPENSE STATISTICS")
    print("="*60)
    print(f"Total Expenses: {stats['total_expenses']}")
    print(f"Total Amount: ${float(stats['total_amount']):,.2f}")
    print(f"Average: ${float(stats['average_expense']):,.2f}")
    
    print("\nBy Category:")
    for cat, amount in stats['by_category'].items():
        print(f"  - {cat.title()}: ${amount:,.2f}")
    
    print("\nBy Payment Method:")
    for method, amount in stats['by_payment_method'].items():
        print(f"  - {method.replace('_', ' ').title()}: ${amount:,.2f}")
    
    # 8. Get User Summary
    print("\n" + "="*60)
    print("👤 USER SUMMARY")
    print("="*60)
    summary = requests.get(
        f"{BASE_URL}/users/{user['id']}/summary",
        headers=HEADERS
    ).json()
    
    print(f"Name: {summary['name']}")
    print(f"Email: {summary['email']}")
    print(f"Total Balance: ${summary['total_balance']}")
    print(f"Savings Accounts: {summary['total_savings_accounts']}")
    print(f"Debit Cards: {summary['total_debit_cards']}")
    print(f"Credit Cards: {summary['total_credit_cards']}")
    print(f"Total Expenses: {summary['total_expenses']}")
    print("="*60)
    
    print("\n✅ Complete test flow finished successfully!")
    
    return {
        "user_id": user['id'],
        "account_id": account['id'],
        "debit_card_id": debit_card['id'],
        "credit_card_id": credit_card['id'],
        "expenses": [expense1['id'], expense2['id'], expense3['id']]
    }

if __name__ == "__main__":
    try:
        ids = test_complete_flow()
        print(f"\n📝 Created IDs:\n{json.dumps(ids, indent=2)}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()