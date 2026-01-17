# api/routers/users.py
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from api.dependencies import get_db, verify_api_key
from api.schemas.user import (
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    UserListResponse,
    UserSummary
)
from api.services.user_service import UserService

router = APIRouter(
    prefix='/users',
    tags=['users'],
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "User Not Found"}}
)

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="create a new user",
    description="create a new user with name and email"
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Create a new user with the following information:
    
    - **name**: User's full name (required)
    - **email**: User's email address (required, must be unique)
    """
    return UserService.create_user(db, user)

@router.get(
    "/",
    response_model=UserListResponse,
    summary="Get list of users",
    description="Retrieve a paginated list of users"
)
def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of users with pagination support:
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 100, max: 1000)
    - **is_active**: Filter by active status (optional)
    """
    users, total = UserService.get_users(db, skip=skip, limit=limit, is_active=is_active)
    return {"total": total, "users": users}

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve a specific user by their ID"
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID
    """
    return UserService.get_user_by_id(db, user_id)

@router.get(
    "/{user_id}/summary",
    response_model=UserSummary,
    summary="Get user financial summary",
    description="Get user details along with financial summary"
)
def get_user_summary(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive user information including:
    - Basic user details
    - Count of savings accounts, debit cards, credit cards
    - Total number of expenses
    - Total balance across all savings accounts
    """
    return UserService.get_user_summary(db, user_id)

@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user information"
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user information. All fields are optional:
    
    - **name**: New name (optional)
    - **email**: New email (optional)
    - **is_active**: Active status (optional)
    """
    return UserService.update_user(db, user_id, user_data)

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user and all related records"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a user. This will cascade delete all related:
    - Savings accounts
    - Debit cards
    - Credit cards
    - Expenses
    """
    UserService.delete_user(db, user_id)