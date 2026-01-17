# api/schemas/expense.py
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum

class PaymentMethod(str, Enum):
    """Enum for payment methods"""
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    CASH = "cash"
    UPI = "upi"
    NET_BANKING = "net_banking"

class ExpenseCategory(str, Enum):
    """Common expense categories"""
    FOOD = "food"
    TRANSPORTATION = "transportation"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    TRAVEL = "travel"
    RENT = "rent"
    GROCERIES = "groceries"
    OTHER = "other"

class ExpenseBase(BaseModel):
    category: ExpenseCategory
    amount: Decimal = Field(..., gt=0)
    payment_method: PaymentMethod
    expense_date: datetime = Field(default_factory=lambda: datetime.now())
    description: Optional[str] = None
    merchant_name: Optional[str] = None
    tags: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    user_id: int = Field(..., gt=0)
    debit_card_id: Optional[int] = Field(None, gt=0)
    credit_card_id: Optional[int] = Field(None, gt=0)
    savings_account_id: Optional[int] = Field(None, gt=0)
    
    
    @model_validator(mode='after')
    def validate_payment_method_and_card(self):
        """Ensure payment method matches provided card"""
        if self.payment_method == PaymentMethod.DEBIT_CARD:
            if not self.debit_card_id:
                raise ValueError("debit_card_id required when payment_method is debit_card")
            if self.credit_card_id:
                raise ValueError("Cannot specify credit_card_id when payment_method is debit_card")
        
        elif self.payment_method == PaymentMethod.CREDIT_CARD:
            if not self.credit_card_id:
                raise ValueError("credit_card_id required when payment_method is credit_card")
            if self.debit_card_id:
                raise ValueError("Cannot specify debit_card_id when payment_method is credit_card")
        elif self.payment_method in [PaymentMethod.UPI, PaymentMethod.NET_BANKING]:
            if not self.savings_account_id:
                raise ValueError(f"savings_account_id required when payment_method is {self.payment_method.value}")
        else:
            # For cash no card should be specified
            if self.debit_card_id or self.credit_card_id:
                raise ValueError(f"No card should be specified for {self.payment_method.value}")
        
        return self

class ExpenseUpdate(BaseModel):
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = None
    merchant_name: Optional[str] = None
    tags: Optional[str] = None

class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    debit_card_id: Optional[int]
    credit_card_id: Optional[int]
    credit_card_transaction_id: Optional[int]
    savings_transaction_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ExpenseWithDetails(ExpenseResponse):
    """Expense with related card/account information"""
    card_name: Optional[str] = None
    account_name: Optional[str] = None
    bank_name: Optional[str] = None

class ExpenseListResponse(BaseModel):
    total: int
    expenses: list[ExpenseResponse]

class ExpenseStatistics(BaseModel):
    """Expense statistics and analytics"""
    total_expenses: int
    total_amount: Decimal
    by_category: dict[str, Decimal]
    by_payment_method: dict[str, Decimal]
    average_expense: Decimal
    date_range: dict[str, datetime]

class ExpenseSummary(BaseModel):
    """Monthly/yearly expense summary"""
    period: str  # e.g., "2024-01" or "2024"
    total_amount: Decimal
    expense_count: int
    top_category: str
    top_merchant: Optional[str]