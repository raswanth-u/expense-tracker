# api/services/credit_card_service.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import HTTPException, status

from db.models import (
    CreditCard, CreditCardTransaction, CreditCardPayment,
    User, SavingsAccount, SavingsTransaction
)
from api.schemas.credit_card import (
    CreditCardCreate, CreditCardUpdate,
    CreditCardTransactionCreate, CreditCardPaymentCreate
)
from settings import setup_logging

logger = setup_logging("credit_card_service", "api.log")

class CreditCardService:
    """Service layer for credit card operations"""
    
    @staticmethod
    def create_card(db: Session, card_data: CreditCardCreate) -> CreditCard:
        """Create a new credit card"""
        logger.info(f"Creating credit card for user_id: {card_data.user_id}")
        
        # Verify user exists
        user = db.query(User).filter(User.id == card_data.user_id).first()
        if not user:
            logger.error(f"User not found: {card_data.user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {card_data.user_id} not found"
            )
        
        # Check if card number already exists
        existing = db.query(CreditCard).filter(
            CreditCard.card_number == card_data.card_number
        ).first()
        
        if existing:
            logger.warning(f"Duplicate card number attempt: {card_data.card_number[-4:]}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Card number already exists"
            )
        
        # Create card with available_credit equal to credit_limit initially
        card_dict = card_data.model_dump()
        card_dict["available_credit"] = card_dict["credit_limit"]
        card_dict["outstanding_balance"] = Decimal("0.00")
        
        card = CreditCard(**card_dict)
        db.add(card)
        db.commit()
        db.refresh(card)
        
        logger.info(f"Credit card created successfully: ID={card.id}, Limit=${card.credit_limit}")
        return card
    
    @staticmethod
    def get_card_by_id(db: Session, card_id: int) -> CreditCard:
        """Get credit card by ID"""
        logger.debug(f"Fetching credit card: {card_id}")
        card = db.query(CreditCard).filter(CreditCard.id == card_id).first()
        if not card:
            logger.error(f"Credit card not found: {card_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credit card with id {card_id} not found"
            )
        return card
    
    @staticmethod
    def get_cards(
        db: Session,
        user_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[CreditCard], int]:
        """Get list of credit cards with filters"""
        logger.debug(f"Fetching credit cards: user_id={user_id}, is_active={is_active}")
        
        query = db.query(CreditCard)
        
        if user_id:
            query = query.filter(CreditCard.user_id == user_id)
        
        if is_active is not None:
            query = query.filter(CreditCard.is_active == is_active)
        
        total = query.count()
        cards = query.offset(skip).limit(limit).all()
        
        logger.info(f"Found {total} credit cards")
        return cards, total
    
    @staticmethod
    def update_card(
        db: Session,
        card_id: int,
        card_data: CreditCardUpdate
    ) -> CreditCard:
        """Update credit card"""
        logger.info(f"Updating credit card: {card_id}")
        card = CreditCardService.get_card_by_id(db, card_id)
        
        update_data = card_data.model_dump(exclude_unset=True)
        
        # If credit limit is being updated, adjust available credit
        if "credit_limit" in update_data:
            old_limit = card.credit_limit
            new_limit = update_data["credit_limit"]
            difference = new_limit - old_limit
            card.available_credit += difference
            logger.info(f"Credit limit updated: ${old_limit} -> ${new_limit}")
        
        for field, value in update_data.items():
            if field != "credit_limit":  # Already handled above
                setattr(card, field, value)
        
        db.commit()
        db.refresh(card)
        logger.info(f"Credit card updated successfully: {card_id}")
        return card
    
    @staticmethod
    def delete_card(db: Session, card_id: int) -> None:
        """Delete credit card"""
        logger.warning(f"Deleting credit card: {card_id}")
        card = CreditCardService.get_card_by_id(db, card_id)
        db.delete(card)
        db.commit()
        logger.info(f"Credit card deleted: {card_id}")
    
    @staticmethod
    def create_transaction(
        db: Session,
        transaction_data: CreditCardTransactionCreate
    ) -> CreditCardTransaction:
        """Create a credit card transaction"""
        logger.info(
            f"Creating transaction: card_id={transaction_data.credit_card_id}, "
            f"type={transaction_data.transaction_type}, amount=${transaction_data.amount}"
        )
        
        card = CreditCardService.get_card_by_id(db, transaction_data.credit_card_id)
        
        # Calculate new outstanding and available credit
        amount = transaction_data.amount
        
        if transaction_data.transaction_type == "refund":
            # Refunds reduce outstanding balance
            new_outstanding = card.outstanding_balance + amount  # amount is negative
            new_available = card.available_credit - amount
        else:
            # Charges increase outstanding balance
            new_outstanding = card.outstanding_balance + amount
            new_available = card.available_credit - amount
        
        # Check if transaction would exceed credit limit
        if new_available < 0:
            logger.error(
                f"Transaction exceeds credit limit: "
                f"available=${card.available_credit}, amount=${amount}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transaction would exceed credit limit. Available: ${card.available_credit}"
            )
        
        # Create transaction
        transaction = CreditCardTransaction(
            credit_card_id=transaction_data.credit_card_id,
            transaction_type=transaction_data.transaction_type.value,
            amount=amount,
            outstanding_after=new_outstanding,
            description=transaction_data.description,
            merchant_name=transaction_data.merchant_name,
            tags=transaction_data.tags
        )
        
        # Update card balances
        card.outstanding_balance = new_outstanding
        card.available_credit = new_available
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        logger.info(
            f"Transaction created: ID={transaction.id}, "
            f"new_outstanding=${new_outstanding}, new_available=${new_available}"
        )
        return transaction
    
    @staticmethod
    def create_payment(
        db: Session,
        payment_data: CreditCardPaymentCreate
    ) -> CreditCardPayment:
        """Create a payment from savings account to credit card"""
        logger.info(
            f"Processing payment: card_id={payment_data.credit_card_id}, "
            f"amount=${payment_data.payment_amount}"
        )
        
        card = CreditCardService.get_card_by_id(db, payment_data.credit_card_id)
        
        # Verify savings account exists
        savings_account = db.query(SavingsAccount).filter(
            SavingsAccount.id == payment_data.savings_account_id
        ).first()
        
        if not savings_account:
            logger.error(f"Savings account not found: {payment_data.savings_account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Savings account with id {payment_data.savings_account_id} not found"
            )
        
        # Check if savings account has sufficient balance
        if savings_account.current_balance < payment_data.payment_amount:
            logger.error(
                f"Insufficient balance: "
                f"available=${savings_account.current_balance}, "
                f"required=${payment_data.payment_amount}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Available: ${savings_account.current_balance}"
            )
        
        # Check payment doesn't exceed outstanding balance
        if payment_data.payment_amount > card.outstanding_balance:
            logger.warning(
                f"Payment exceeds outstanding: "
                f"payment=${payment_data.payment_amount}, "
                f"outstanding=${card.outstanding_balance}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment exceeds outstanding balance of ${card.outstanding_balance}"
            )
        
        outstanding_before = card.outstanding_balance
        outstanding_after = outstanding_before - payment_data.payment_amount
        
        # Create savings transaction (withdrawal)
        savings_transaction = SavingsTransaction(
            savings_account_id=payment_data.savings_account_id,
            transaction_type="credit_card_payment",
            amount=payment_data.payment_amount,
            balance_after=savings_account.current_balance - payment_data.payment_amount,
            description=f"Credit card payment: {card.card_name}"
        )
        
        # Update savings account balance
        savings_account.current_balance -= payment_data.payment_amount
        
        # Create credit card payment
        payment = CreditCardPayment(
            credit_card_id=payment_data.credit_card_id,
            savings_account_id=payment_data.savings_account_id,
            payment_amount=payment_data.payment_amount,
            outstanding_before=outstanding_before,
            outstanding_after=outstanding_after,
            payment_method=payment_data.payment_method.value,
            description=payment_data.description
        )
        
        # Update credit card balances
        card.outstanding_balance = outstanding_after
        card.available_credit += payment_data.payment_amount
        
        db.add(savings_transaction)
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # Link savings transaction to payment
        payment.savings_transaction_id = savings_transaction.id
        db.commit()
        
        logger.info(
            f"Payment processed: ID={payment.id}, "
            f"outstanding: ${outstanding_before} -> ${outstanding_after}"
        )
        return payment
    
    @staticmethod
    def get_transactions(
        db: Session,
        card_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[CreditCardTransaction], int]:
        """Get transactions for a card"""
        logger.debug(f"Fetching transactions for card: {card_id}")
        CreditCardService.get_card_by_id(db, card_id)
        
        query = db.query(CreditCardTransaction).filter(
            CreditCardTransaction.credit_card_id == card_id
        ).order_by(CreditCardTransaction.transaction_date.desc())
        
        total = query.count()
        transactions = query.offset(skip).limit(limit).all()
        
        logger.info(f"Found {total} transactions for card {card_id}")
        return transactions, total
    
    @staticmethod
    def get_payments(
        db: Session,
        card_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[CreditCardPayment], int]:
        """Get payments for a card"""
        logger.debug(f"Fetching payments for card: {card_id}")
        CreditCardService.get_card_by_id(db, card_id)
        
        query = db.query(CreditCardPayment).filter(
            CreditCardPayment.credit_card_id == card_id
        ).order_by(CreditCardPayment.payment_date.desc())
        
        total = query.count()
        payments = query.offset(skip).limit(limit).all()
        
        logger.info(f"Found {total} payments for card {card_id}")
        return payments, total