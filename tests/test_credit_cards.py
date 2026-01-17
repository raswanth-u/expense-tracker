# scripts/test_flow.py
"""
Complete test flow for the expense tracker application
# Credit Card Testing Checklist

## Basic Operations
- [ ] Create credit card
- [ ] List all cards
- [ ] List cards by user
- [ ] View card details
- [ ] Update card (credit limit, rates)
- [ ] Delete card

## Transactions
- [ ] Create purchase transaction
- [ ] Create refund transaction
- [ ] Create interest charge
- [ ] Create late fee
- [ ] Create annual fee
- [ ] View transaction history
- [ ] Verify outstanding balance updates
- [ ] Verify available credit updates

## Payments
- [ ] Make payment from savings account
- [ ] Verify savings account balance decreases
- [ ] Verify credit card outstanding decreases
- [ ] Verify available credit increases
- [ ] View payment history
- [ ] Test payment exceeding outstanding (should fail)
- [ ] Test payment with insufficient savings balance (should fail)

## Edge Cases
- [ ] Transaction exceeding credit limit (should fail)
- [ ] Payment without outstanding balance (should fail)
- [ ] Create card with duplicate card number (should fail)
- [ ] Update credit limit (verify available credit adjusts)
- [ ] Multiple transactions and payments
- [ ] Delete card with outstanding balance (should work with warning)

## Logging
- [ ] Check API logs for all operations
- [ ] Check database logs for queries
- [ ] Check CLI logs for user actions
- [ ] Verify slow query warnings (>1s)
- [ ] Verify error logging with stack traces
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "your-secret-api-key"
HEADERS = {"X-API-Key": API_KEY}

def create_test_data():
    """Create complete test data flow"""
    
    print("🚀 Starting test data creation...\n")
    
    # 1. Create User
    print("1️⃣ Creating user...")
    user_data = {
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
    user_response = requests.post(
        f"{BASE_URL}/users/",
        json=user_data,
        headers=HEADERS
    )
    user = user_response.json()
    print(f"   ✅ User created: ID={user['id']}, Name={user['name']}\n")
    
    # 2. Create Savings Account
    print("2️⃣ Creating savings account...")
    account_data = {
        "user_id": user['id'],
        "account_name": "Primary Savings",
        "bank_name": "HDFC Bank",
        "account_number": "1234567890",
        "account_type": "savings",
        "minimum_balance": 1000.00,
        "current_balance": 50000.00,
        "interest_rate": 4.5
    }
    account_response = requests.post(
        f"{BASE_URL}/savings-accounts/",
        json=account_data,
        headers=HEADERS
    )
    account = account_response.json()
    print(f"   ✅ Account created: ID={account['id']}, Balance=${account['current_balance']}\n")
    
    # 3. Create Debit Card
    print("3️⃣ Creating debit card...")
    debit_card_data = {
        "user_id": user['id'],
        "savings_account_id": account['id'],
        "card_name": "HDFC Debit Card",
        "card_number": "4111111111111111",
        "card_type": "visa"
    }
    debit_response = requests.post(
        f"{BASE_URL}/debit-cards/",
        json=debit_card_data,
        headers=HEADERS
    )
    debit_card = debit_response.json()
    print(f"   ✅ Debit card created: ID={debit_card['id']}\n")
    
    # 4. Create Credit Card
    print("4️⃣ Creating credit card...")
    credit_card_data = {
        "user_id": user['id'],
        "card_name": "HDFC Regalia",
        "card_number": "5555555555554444",
        "card_type": "mastercard",
        "credit_limit": 100000.00,
        "billing_cycle_day": 1,
        "payment_due_day": 20,
        "interest_rate": 3.5,
        "minimum_payment_percentage": 5.0
    }
    credit_response = requests.post(
        f"{BASE_URL}/credit-cards/",
        json=credit_card_data,
        headers=HEADERS
    )
    credit_card = credit_response.json()
    print(f"   ✅ Credit card created: ID={credit_card['id']}, Limit=${credit_card['credit_limit']}\n")
    
    # 5. Create Credit Card Transaction (Purchase)
    print("5️⃣ Creating credit card purchase...")
    transaction_data = {
        "credit_card_id": credit_card['id'],
        "transaction_type": "purchase",
        "amount": 15000.00,
        "merchant_name": "Amazon",
        "description": "Laptop purchase"
    }
    txn_response = requests.post(
        f"{BASE_URL}/credit-cards/transactions",
        json=transaction_data,
        headers=HEADERS
    )
    transaction = txn_response.json()
    print(f"   ✅ Transaction created: ID={transaction['id']}, Amount=${transaction['amount']}\n")
    
    # 6. Make Payment
    print("6️⃣ Making credit card payment...")
    payment_data = {
        "credit_card_id": credit_card['id'],
        "savings_account_id": account['id'],
        "payment_amount": 5000.00,
        "payment_method": "net_banking",
        "description": "Partial payment"
    }
    payment_response = requests.post(
        f"{BASE_URL}/credit-cards/payments",
        json=payment_data,
        headers=HEADERS
    )
    payment = payment_response.json()
    print(f"   ✅ Payment processed: ID={payment['id']}, Amount=${payment['payment_amount']}\n")
    
    # 7. Get User Summary
    print("7️⃣ Getting user summary...")
    summary_response = requests.get(
        f"{BASE_URL}/users/{user['id']}/summary",
        headers=HEADERS
    )
    summary = summary_response.json()
    
    print("\n" + "="*60)
    print("📊 USER SUMMARY")
    print("="*60)
    print(f"Name: {summary['name']}")
    print(f"Email: {summary['email']}")
    print(f"Total Balance: ${summary['total_balance']}")
    print(f"Savings Accounts: {summary['total_savings_accounts']}")
    print(f"Debit Cards: {summary['total_debit_cards']}")
    print(f"Credit Cards: {summary['total_credit_cards']}")
    print("="*60)
    
    print("\n✅ Test data creation completed successfully!")
    
    return {
        "user_id": user['id'],
        "account_id": account['id'],
        "debit_card_id": debit_card['id'],
        "credit_card_id": credit_card['id']
    }

if __name__ == "__main__":
    try:
        ids = create_test_data()
        print(f"\n📝 Created IDs: {json.dumps(ids, indent=2)}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")