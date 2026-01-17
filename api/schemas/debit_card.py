# api/schemas/debit_card.py

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum

class CardType(str, Enum):
    """Enum for card types"""
    VISA = "visa"
    MASTERCARD = "mastercard"
    RUPAY = "rupay"
    
class DebitCardBase(BaseModel):
    card_name: str = Field(..., min_length=1, max_length=100)
    card_number: str = Field(..., min_length=13, max_length=19)
    card_type: CardType
    expiry_date: Optional[datetime] = None
    is_active: bool = True
    tags: Optional[str] = None
    
    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        """Validate card number contains only digits"""
        if not v.isdigit():
            raise ValueError("Card number must contain only digits")
        return v
    
class DebitCardCreate(DebitCardBase):
    user_id: int = Field(..., gt=0)
    savings_account_id: int = Field(..., gt=0)
    
class DebitCardUpdate(BaseModel):
    card_name: Optional[str] = Field(None, min_length=1, max_length=100)
    expiry_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    tags: Optional[str] = None
    
class DebitCardResponse(DebitCardBase):
    id: int
    user_id: int
    savings_account_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class DebitCardWithDetails(DebitCardResponse):
    """Debit card with related account info"""
    account_name: Optional[str] = None
    bank_name: Optional[str] = None
    current_balance: Optional[float] = None
    
class DebitCardListResponse(BaseModel):
    total: int
    cards: list[DebitCardResponse]

