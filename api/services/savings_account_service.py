# api/services/savings_account_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import HTTPException, status

from db.models import SavingsAccount, SavingsTransaction, User
from api.schemas.savings_account import (
    SavingsAccountCreate, 
    SavingsAccountUpdate,
    SavingsTransactionCreate
)

class SavingsAccountService:
    """Service layer for savings account operations"""
    
    @staticmethod
    def create_account(db: Session, account_data: SavingsAccountCreate) -> SavingsAccount:
        """ Create a new savings account """
        # Verify user exists
        user = db.query(User).filter(User.id == account_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {account_data.user_id} not found"
            )
            
        # Check if account number already exists
        existing = db.query(SavingsAccount).filter(
            SavingsAccount.account_number == account_data.account_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account number already exists"
            )
            
        # create account
        account = SavingsAccount(**account_data.model_dump())
        db.add(account)
        db.commit()
        db.refresh(account)
        return account
    
    @staticmethod
    def get_account_by_id(db: Session, account_id: int) -> SavingsAccount:
        """Get account by ID"""
        account = db.query(SavingsAccount).filter(SavingsAccount.id == account_id).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account with id {account_id} not found"
            )
        return account
    
    @staticmethod
    def get_accounts(
        db: Session,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[SavingsAccount], int]:
        """Get list of accounts with optional user filter"""
        query = db.query(SavingsAccount)
        
        if user_id:
            query = query.filter(SavingsAccount.user_id == user_id)
        
        total = query.count()
        accounts = query.offset(skip).limit(limit).all()
        
        return accounts, total
    
    @staticmethod
    def update_account(
        db: Session, 
        account_id: int, 
        account_data: SavingsAccountUpdate
    ) -> SavingsAccount:
        """Update account details"""
        account = SavingsAccountService.get_account_by_id(db, account_id)
        
        update_data = account_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(account, field, value)
        
        db.commit()
        db.refresh(account)
        return account
    
    @staticmethod
    def delete_account(db: Session, account_id: int) -> None:
        """Delete account"""
        account = SavingsAccountService.get_account_by_id(db, account_id)
        if account:
            db.delete(account)
            db.commit()
            return
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with id {account_id} not found and cannot be deleted"
        )
        
    @staticmethod
    def create_transaction(
        db: Session,
        transaction_data: SavingsTransactionCreate
    ) -> SavingsTransaction:
        """ Create a transaction (deposit/withdrawal) """
        account = SavingsAccountService.get_account_by_id(db, transaction_data.savings_account_id)
        
        # calculate new balance
        if transaction_data.transaction_type in ["deposit", "interest"]:
            new_balance = account.current_balance + transaction_data.amount
        elif transaction_data.transaction_type in ["withdrawal", "debit_card", "credit_card_payment", "upi"]:
            new_balance = account.current_balance - transaction_data.amount
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid transaction type"
            )
            
        transaction = SavingsTransaction(
            savings_account_id=transaction_data.savings_account_id,
            transaction_type=transaction_data.transaction_type,
            amount=transaction_data.amount,
            balance_after=new_balance,
            description=transaction_data.description,
            tags=transaction_data.tags,
            transaction_date=transaction_data.transaction_date,
        )
        
        account.current_balance = new_balance
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        db.refresh(account)
        return transaction
    
    @staticmethod
    def get_transactions(
        db: Session,
        account_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[SavingsTransaction], int]:
        """Get transactions for an account"""
        # Verify account exists
        SavingsAccountService.get_account_by_id(db, account_id)
        
        query = db.query(SavingsTransaction).filter(
            SavingsTransaction.savings_account_id == account_id
        ).order_by(SavingsTransaction.transaction_date.desc())
        
        total = query.count()
        transactions = query.offset(skip).limit(limit).all()
        
        return transactions, total