# api/schemas/savings_account.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal

# Base Schema
class SavingsAccountBase(BaseModel):
    account_name: str = Field(..., min_length=1, max_length=100)
    bank_name: str = Field(..., min_length=1, max_length=100)
    account_number: str = Field(..., min_length=1, max_length=50)
    account_type: str = Field(..., description="Type: savings, current, etc.")
    minimum_balance: Decimal = Field(default=Decimal("0.00"), ge=0)
    current_balance: Decimal = Field(default=Decimal("0.00"), ge=0)
    interest_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    tags: Optional[str] = None
    
# Create schema
class SavingsAccountCreate(SavingsAccountBase):
    user_id: int = Field(..., gt=0)
    
# Update schema
class SavingsAccountUpdate(BaseModel):
    account_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bank_name: Optional[str] = Field(None, min_length=1, max_length=100)
    account_number: Optional[str] = Field(None, min_length=1, max_length=50)
    account_type: Optional[str] = None
    minimum_balance: Optional[Decimal] = Field(None, ge=0)
    current_balance: Optional[Decimal] = Field(None, ge=0)
    interest_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    tags: Optional[str] = None
    
# Response schema
class SavingsAccountResponse(SavingsAccountBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
# List response
class SavingsAccountListResponse(BaseModel):
    total: int
    accounts: list[SavingsAccountResponse]
    
# Transaction schemas
class SavingsTransactionCreate(BaseModel):
    savings_account_id: int = Field(..., gt=0)
    transaction_type: str = Field(..., description="deposit, withdrawal, interest, credit_card_payment, debit_card, upi")
    amount: Decimal = Field(..., gt=0)
    transaction_date: datetime = Field(..., description="transaction date")
    description: Optional[str] = None
    tags: Optional[str] = None
    
class SavingsTransactionResponse(BaseModel):
    id: int
    savings_account_id: int
    transaction_type: str
    amount: Decimal
    balance_after: Decimal
    transaction_date: datetime
    description: Optional[str]
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class SavingsTransactionListResponse(BaseModel):
    total: int
    transactions: list[SavingsTransactionResponse]