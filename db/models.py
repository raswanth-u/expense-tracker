# db/models.py
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Integer, String, Numeric, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import declarative_base

BaseModel = declarative_base()

class User(BaseModel):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True, nullable=False)
    
    savings_accounts = relationship("SavingsAccount", back_populates="user", cascade="all, delete-orphan")
    debit_cards = relationship("DebitCard", back_populates="user", cascade="all, delete-orphan")
    credit_cards = relationship("CreditCard", back_populates="user", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")

class SavingsAccount(BaseModel):
    __tablename__ = "savings_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_name = Column(String, nullable=False)
    bank_name = Column(String, nullable=False)
    account_number = Column(String, unique=True, index=True, nullable=False)
    account_type = Column(String, nullable=False)
    minimum_balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    current_balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    interest_rate = Column(Numeric(5, 2), default=0.00, nullable=False)
    tags = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        CheckConstraint('current_balance >= 0', name='check_positive_balance'),
        CheckConstraint('minimum_balance >= 0', name='check_positive_min_balance'),
    )
    
    user = relationship("User", back_populates="savings_accounts")
    transactions = relationship("SavingsTransaction", back_populates="savings_account", cascade="all, delete-orphan")
    debit_cards = relationship("DebitCard", back_populates="savings_account", cascade="all, delete-orphan")
    credit_card_payments = relationship("CreditCardPayment", back_populates="savings_account")
    expenses = relationship("Expense", back_populates="savings_account")

class SavingsTransaction(BaseModel):
    __tablename__ = "savings_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    savings_account_id = Column(Integer, ForeignKey("savings_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type = Column(String, nullable=False)  # deposit, withdrawal, interest, credit_card_payment
    amount = Column(Numeric(15, 2), nullable=False)
    balance_after = Column(Numeric(15, 2), nullable=False)
    transaction_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    description = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (CheckConstraint('amount > 0', name='check_positive_amount'),)
    
    savings_account = relationship("SavingsAccount", back_populates="transactions")
    expense = relationship("Expense", back_populates="savings_transaction", uselist=False)
    credit_card_payment = relationship("CreditCardPayment", back_populates="savings_transaction", uselist=False)

class DebitCard(BaseModel):
    __tablename__ = "debit_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    savings_account_id = Column(Integer, ForeignKey("savings_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    card_name = Column(String, nullable=False)
    card_number = Column(String, unique=True, index=True, nullable=False)
    card_type = Column(String, nullable=False)  # visa, mastercard, rupay
    expiry_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    tags = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="debit_cards")
    savings_account = relationship("SavingsAccount", back_populates="debit_cards")
    expenses = relationship("Expense", back_populates="debit_card")

class CreditCard(BaseModel):
    __tablename__ = "credit_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    card_name = Column(String, nullable=False)
    card_number = Column(String, unique=True, index=True, nullable=False)
    card_type = Column(String, nullable=False)  # visa, mastercard, rupay, amex
    credit_limit = Column(Numeric(15, 2), nullable=False)
    available_credit = Column(Numeric(15, 2), nullable=False)
    outstanding_balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    billing_cycle_day = Column(Integer, nullable=False)  # 1-31
    payment_due_day = Column(Integer, nullable=False)  # 1-31
    interest_rate = Column(Numeric(5, 2), default=0.00, nullable=False)
    minimum_payment_percentage = Column(Numeric(5, 2), default=5.00, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    tags = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        CheckConstraint('credit_limit > 0', name='check_positive_credit_limit'),
        CheckConstraint('available_credit >= 0 AND available_credit <= credit_limit', name='check_valid_available_credit'),
        CheckConstraint('outstanding_balance >= 0', name='check_positive_outstanding'),
    )
    
    user = relationship("User", back_populates="credit_cards")
    expenses = relationship("Expense", back_populates="credit_card")
    transactions = relationship("CreditCardTransaction", back_populates="credit_card", cascade="all, delete-orphan")
    payments = relationship("CreditCardPayment", back_populates="credit_card", cascade="all, delete-orphan")
    statements = relationship("CreditCardStatement", back_populates="credit_card", cascade="all, delete-orphan")

class CreditCardTransaction(BaseModel):
    __tablename__ = "credit_card_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    credit_card_id = Column(Integer, ForeignKey("credit_cards.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type = Column(String, nullable=False)  # purchase, refund, interest_charge, late_fee, annual_fee
    amount = Column(Numeric(15, 2), nullable=False)
    outstanding_after = Column(Numeric(15, 2), nullable=False)
    transaction_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    description = Column(String, nullable=True)
    merchant_name = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (CheckConstraint('amount != 0', name='check_nonzero_amount'),)
    
    credit_card = relationship("CreditCard", back_populates="transactions")
    expense = relationship("Expense", back_populates="credit_card_transaction", uselist=False)

class CreditCardPayment(BaseModel):
    __tablename__ = "credit_card_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    credit_card_id = Column(Integer, ForeignKey("credit_cards.id", ondelete="CASCADE"), nullable=False, index=True)
    savings_account_id = Column(Integer, ForeignKey("savings_accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    savings_transaction_id = Column(Integer, ForeignKey("savings_transactions.id", ondelete="SET NULL"), nullable=True, index=True)
    payment_amount = Column(Numeric(15, 2), nullable=False)
    outstanding_before = Column(Numeric(15, 2), nullable=False)
    outstanding_after = Column(Numeric(15, 2), nullable=False)
    payment_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    payment_method = Column(String, nullable=False)  # auto_debit, manual, net_banking
    description = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (CheckConstraint('payment_amount > 0', name='check_positive_payment'),)
    
    credit_card = relationship("CreditCard", back_populates="payments")
    savings_account = relationship("SavingsAccount", back_populates="credit_card_payments")
    savings_transaction = relationship("SavingsTransaction", back_populates="credit_card_payment")

class CreditCardStatement(BaseModel):
    __tablename__ = "credit_card_statements"
    
    id = Column(Integer, primary_key=True, index=True)
    credit_card_id = Column(Integer, ForeignKey("credit_cards.id", ondelete="CASCADE"), nullable=False, index=True)
    statement_date = Column(DateTime, nullable=False, index=True)
    due_date = Column(DateTime, nullable=False, index=True)
    previous_balance = Column(Numeric(15, 2), nullable=False)
    total_purchases = Column(Numeric(15, 2), default=0.00, nullable=False)
    total_payments = Column(Numeric(15, 2), default=0.00, nullable=False)
    total_fees = Column(Numeric(15, 2), default=0.00, nullable=False)
    total_interest = Column(Numeric(15, 2), default=0.00, nullable=False)
    closing_balance = Column(Numeric(15, 2), nullable=False)
    minimum_payment_due = Column(Numeric(15, 2), nullable=False)
    is_paid = Column(Boolean, default=False, nullable=False)
    paid_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    credit_card = relationship("CreditCard", back_populates="statements")

class Expense(BaseModel):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    savings_account_id = Column(Integer, ForeignKey("savings_accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    debit_card_id = Column(Integer, ForeignKey("debit_cards.id", ondelete="SET NULL"), nullable=True, index=True)
    credit_card_id = Column(Integer, ForeignKey("credit_cards.id", ondelete="SET NULL"), nullable=True, index=True)
    credit_card_transaction_id = Column(Integer, ForeignKey("credit_card_transactions.id", ondelete="SET NULL"), nullable=True, index=True)
    savings_transaction_id = Column(Integer, ForeignKey("savings_transactions.id", ondelete="SET NULL"), nullable=True, index=True)
    category = Column(String, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String, nullable=False)  # debit_card, credit_card, cash, upi, net_banking
    expense_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    description = Column(String, nullable=True)
    merchant_name = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    created_at = Column(# The above code appears to be a comment in Python. It starts with a "#"
    # symbol, which indicates that it is a single-line comment. The text
    # "DateTime" seems to be a heading or label for the following code or
    # explanation. The "
    DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (CheckConstraint('amount > 0', name='check_positive_expense_amount'),)
    
    user = relationship("User", back_populates="expenses")
    debit_card = relationship("DebitCard", back_populates="expenses")
    credit_card = relationship("CreditCard", back_populates="expenses")
    credit_card_transaction = relationship("CreditCardTransaction", back_populates="expense")
    savings_transaction = relationship("SavingsTransaction", back_populates="expense")
    savings_account = relationship("SavingsAccount", back_populates="expenses")
    
# Export all models for easy importing
__all__ = [
    'BaseModel',
    'User',
    'SavingsAccount',
    'SavingsTransaction',
    'DebitCard',
    'CreditCard',
    'CreditCardTransaction',
    'CreditCardPayment',
    'CreditCardStatement',
    'Expense'
]