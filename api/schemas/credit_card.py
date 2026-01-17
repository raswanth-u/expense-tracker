# api/schemas/credit_card.py
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum

class CardType(str, Enum):
    """Enum for credit card types"""
    VISA = "visa"
    MASTERCARD = "mastercard"
    RUPAY = "rupay"
    AMEX = "amex"
    
class CreditCardBase(BaseModel):
    card_name: str = Field(..., min_length=1, max_length=100)
    card_number: str = Field(..., min_length=13, max_length=19)
    card_type: CardType
    credit_limit: Decimal = Field(..., gt=0)
    billing_cycle_day: int = Field(..., ge=1, le=31)
    payment_due_day: int = Field(..., ge=1, le=31)
    interest_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    minimum_payment_percentage: Decimal = Field(default=Decimal("5.00"), ge=0, le=100)
    expiry_date: Optional[datetime] = None
    is_active: bool = True
    tags: Optional[str] = None
    
    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Card number must contain only digits")
        return v
    
    @field_validator("payment_due_day")
    @classmethod
    def validate_payment_due_day(cls, v: int, info) -> int:
        if "billing_cycle_day" in info.data and v <= info.data["billing_cycle_day"]:
            raise ValueError("Payment due day must be after billing cycle day")
        return v
    
class CreditCardCreate(CreditCardBase):
    user_id: int = Field(..., gt=0)
    
class CreditCardUpdate(BaseModel):
    card_name: Optional[str] = Field(None, min_length=1, max_length=100)
    credit_limit: Optional[Decimal] = Field(None, gt=0)
    interest_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    minimum_payment_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    expiry_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    tags: Optional[str] = None
    
class CreditCardResponse(CreditCardBase):
    id: int
    user_id: int
    available_credit: Decimal
    outstanding_balance: Decimal
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class CreditCardListResponse(BaseModel):
    total: int
    cards: list[CreditCardResponse]
    
# Transaction schemas
class TransactionType(str, Enum):
    PURCHASE = "purchase"
    REFUND = "refund"
    INTEREST_CHARGE = "interest_charge"
    LATE_FEE = "late_fee"
    ANNUAL_FEE = "annual_fee"
    
class CreditCardTransactionCreate(BaseModel):
    credit_card_id: int = Field(..., gt=0)
    transaction_type: TransactionType
    amount: Decimal = Field(..., description="Positive for charges, negative for refunds")
    description: Optional[str] = None
    merchant_name: Optional[str] = None
    tags: Optional[str] = None
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal, info) -> Decimal:
        if v == 0:
            raise ValueError("Amount cannot be zero")
        if "transaction_type" in info.data:
            if info.data["transaction_type"] == TransactionType.REFUND and v > 0:
                return -v  # Auto-convert refunds to negative
        return v
    
class CreditCardTransactionResponse(BaseModel):
    id: int
    credit_card_id: int
    transaction_type: str
    amount: Decimal
    outstanding_after: Decimal
    transaction_date: datetime
    description: Optional[str]
    merchant_name: Optional[str]
    tags: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class CreditCardTransactionListResponse(BaseModel):
    total: int
    transactions: list[CreditCardTransactionResponse]
    
# Payment schemas
class PaymentMethod(str, Enum):
    AUTO_DEBIT = "auto_debit"
    MANUAL = "manual"
    NET_BANKING = "net_banking"

class CreditCardPaymentCreate(BaseModel):
    credit_card_id: int = Field(..., gt=0)
    savings_account_id: int = Field(..., gt=0)
    payment_amount: Decimal = Field(..., gt=0)
    payment_method: PaymentMethod
    description: Optional[str] = None
    
class CreditCardPaymentResponse(BaseModel):
    id: int
    credit_card_id: int
    savings_account_id: Optional[int]
    payment_amount: Decimal
    outstanding_before: Decimal
    outstanding_after: Decimal
    payment_date: datetime
    payment_method: str
    description: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class CreditCardPaymentListResponse(BaseModel):
    total: int
    payments: list[CreditCardPaymentResponse]