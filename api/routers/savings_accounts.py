# api/routers/savings_accounts.py
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from api.dependencies import get_db, verify_api_key
from api.schemas.savings_account import (
    SavingsAccountCreate,
    SavingsAccountUpdate,
    SavingsAccountResponse,
    SavingsAccountListResponse,
    SavingsTransactionCreate,
    SavingsTransactionResponse,
    SavingsTransactionListResponse
)
from api.services.savings_account_service import SavingsAccountService

router = APIRouter(
    prefix="/savings-accounts",
    tags=["savings-accounts"],
    dependencies=[Depends(verify_api_key)],
)

@router.post(
    "/",
    response_model=SavingsAccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create savings account"
)
def create_account(
    account: SavingsAccountCreate,
    db: Session = Depends(get_db)
):
    """Create a new savings account"""
    return SavingsAccountService.create_account(db, account)

@router.get(
    "/",
    response_model=SavingsAccountListResponse,
    summary="List savings accounts"
)
def get_accounts(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get list of savings accounts"""
    accounts, total = SavingsAccountService.get_accounts(db, user_id, skip, limit)
    return {"total": total, "accounts": accounts}

@router.get(
    "/{account_id}",
    response_model=SavingsAccountResponse,
    summary="Get savings account"
)
def get_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Get savings account by ID"""
    return SavingsAccountService.get_account_by_id(db, account_id)

@router.put(
    "/{account_id}",
    response_model=SavingsAccountResponse,
    summary="Update savings account"
)
def update_account(
    account_id: int,
    account_data: SavingsAccountUpdate,
    db: Session = Depends(get_db)
):
    """Update savings account"""
    return SavingsAccountService.update_account(db, account_id, account_data)

@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete savings account"
)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Delete savings account"""
    SavingsAccountService.delete_account(db, account_id)
    
# Transaction endpoints
@router.post(
    "/transactions",
    response_model=SavingsTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create transaction"
)
def create_transaction(
    transaction: SavingsTransactionCreate,
    db: Session = Depends(get_db)
):
    """Create a deposit or withdrawal transaction"""
    return SavingsAccountService.create_transaction(db, transaction)

@router.get(
    "/{account_id}/transactions",
    response_model=SavingsTransactionListResponse,
    summary="Get account transactions"
)
def get_transactions(
    account_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get transactions for an account"""
    transactions, total = SavingsAccountService.get_transactions(db, account_id, skip, limit)
    return {"total": total, "transactions": transactions}