# api/routers/expenses.py
from fastapi import APIRouter, Depends, Query, status, Path
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from decimal import Decimal

from api.dependencies import get_db, verify_api_key
from api.schemas.expense import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseWithDetails,
    ExpenseListResponse, ExpenseStatistics, ExpenseSummary,
    ExpenseCategory, PaymentMethod
)
from api.services.expense_service import ExpenseService
from settings import setup_logging

logger = setup_logging("expense_router", "api.log")

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
    dependencies=[Depends(verify_api_key)],
)

@router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create expense"
)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db)
) -> ExpenseResponse:
    """
    Create a new expense with automatic accounting:
    - Debit card: Deducts from linked savings account
    - Credit card: Adds to credit card outstanding
    - Cash/UPI/Net Banking: Simple record without account impact
    """
    logger.info(f"API: Creating expense for user {expense.user_id}")
    result = ExpenseService.create_expense(db, expense)
    logger.info(f"API: Expense created with ID {result.id}")
    return result

@router.get(
    "/",
    response_model=ExpenseListResponse,
    summary="List expenses"
)
def get_expenses(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    category: Optional[ExpenseCategory] = Query(None, description="Filter by category"),
    payment_method: Optional[PaymentMethod] = Query(None, description="Filter by payment method"),
    start_date: Optional[datetime] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="End date (YYYY-MM-DD)"),
    min_amount: Optional[Decimal] = Query(None, ge=0, description="Minimum amount"),
    max_amount: Optional[Decimal] = Query(None, ge=0, description="Maximum amount"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> ExpenseListResponse:
    """Get list of expenses with various filters"""
    logger.debug(
        f"API: Listing expenses (user_id={user_id}, category={category}, "
        f"method={payment_method})"
    )
    
    expenses, total = ExpenseService.get_expenses(
        db, user_id,
        category.value if category else None,
        payment_method.value if payment_method else None,
        start_date, end_date, min_amount, max_amount,
        skip, limit
    )
    
    return ExpenseListResponse(total=total, expenses=expenses)

@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Get expense"
)
def get_expense(
    expense_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
) -> ExpenseResponse:
    """Get expense by ID"""
    logger.debug(f"API: Fetching expense {expense_id}")
    return ExpenseService.get_expense_by_id(db, expense_id)

@router.get(
    "/{expense_id}/details",
    response_model=ExpenseWithDetails,
    summary="Get expense with details"
)
def get_expense_with_details(
    expense_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
) -> ExpenseWithDetails:
    """Get expense with card/account information"""
    logger.debug(f"API: Fetching expense details {expense_id}")
    return ExpenseService.get_expense_with_details(db, expense_id)

@router.put(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Update expense"
)
def update_expense(
    expense_id: int = Path(..., gt=0),
    expense_data: ExpenseUpdate = ...,
    db: Session = Depends(get_db)
) -> ExpenseResponse:
    """Update expense (limited fields only)"""
    logger.info(f"API: Updating expense {expense_id}")
    return ExpenseService.update_expense(db, expense_id, expense_data)

@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete expense"
)
def delete_expense(
    expense_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete expense
    WARNING: This doesn't reverse financial transactions.
    Use with caution.
    """
    logger.warning(f"API: Deleting expense {expense_id}")
    ExpenseService.delete_expense(db, expense_id)

@router.get(
    "/statistics/user/{user_id}",
    response_model=ExpenseStatistics,
    summary="Get expense statistics"
)
def get_statistics(
    user_id: int = Path(..., gt=0),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db)
) -> ExpenseStatistics:
    """Get expense statistics for a user"""
    logger.debug(f"API: Getting statistics for user {user_id}")
    return ExpenseService.get_statistics(db, user_id, start_date, end_date)

@router.get(
    "/summary/user/{user_id}/{year}/{month}",
    response_model=ExpenseSummary,
    summary="Get monthly summary"
)
def get_monthly_summary(
    user_id: int = Path(..., gt=0),
    year: int = Path(..., ge=2000, le=2100),
    month: int = Path(..., ge=1, le=12),
    db: Session = Depends(get_db)
) -> ExpenseSummary:
    """Get monthly expense summary"""
    logger.debug(f"API: Getting monthly summary for user {user_id}, {year}-{month:02d}")
    return ExpenseService.get_monthly_summary(db, user_id, year, month)