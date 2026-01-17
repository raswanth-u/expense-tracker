# api/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Base schema with common fields
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User's Full Name")
    email: EmailStr = Field(..., description="User's email address")
    
# Schema for creating a user (POST request)
class UserCreate(UserBase):
    """Schema for creating a new user"""
    pass

# Schema for updating a user (PUT/PATCH request)
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    
# Schema for response (GET request)
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
    
# Schema for user list response
class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    total: int
    users: list[UserResponse]
    
# Schema for user summary (with related data counts)
class UserSummary(UserResponse):
    """Schema for user with financial summary"""
    total_savings_accounts: int = 0
    total_debit_cards: int = 0
    total_credit_cards: int = 0
    total_expenses: int = 0
    total_balance: float = 0.0
    
    model_config = ConfigDict(from_attributes=True)