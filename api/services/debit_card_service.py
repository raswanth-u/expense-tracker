# app/services/debit_card_service.py
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status

from db.models import DebitCard, User, SavingsAccount
from api.schemas.debit_card import DebitCardCreate, DebitCardUpdate

class DebitCardService:
    """Service layer for debit card operations"""

    @staticmethod
    def create_card(db: Session, card_data: DebitCardCreate) -> DebitCard:
        """Create a new debit card"""
        # Verify user exists
        user = db.query(User).filter(User.id == card_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {card_data.user_id} not found"
            )
        
        # Verify savings account exists and belongs to user
        account = db.query(SavingsAccount).filter(
            SavingsAccount.id == card_data.savings_account_id,
            SavingsAccount.user_id == card_data.user_id
        ).first()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Savings account {card_data.savings_account_id} not found or doesn't belong to user"
            )
        
        # Check if card number already exists
        existing = db.query(DebitCard).filter(
            DebitCard.card_number == card_data.card_number
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Card number already exists"
            )
        
        # Create card
        card = DebitCard(**card_data.model_dump())
        db.add(card)
        db.commit()
        db.refresh(card)
        return card

    @staticmethod
    def get_card_by_id(db: Session, card_id: int) -> DebitCard:
        """Get debit card by ID"""
        card = db.query(DebitCard).filter(DebitCard.id == card_id).first()
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Debit card with id {card_id} not found"
            )
        return card
    
    @staticmethod
    def get_cards(
        db: Session,
        user_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[DebitCard], int]:
        """Get list of debit cards with optional filters"""
        query = db.query(DebitCard)
        
        if user_id:
            query = query.filter(DebitCard.user_id == user_id)
        
        if is_active is not None:
            query = query.filter(DebitCard.is_active == is_active)
        
        total = query.count()
        cards = query.offset(skip).limit(limit).all()
        
        return cards, total
    
    @staticmethod
    def get_card_with_details(db: Session, card_id: int) -> dict:
        """Get debit card with savings account details"""
        card = db.query(DebitCard).options(
            joinedload(DebitCard.savings_account)
        ).filter(DebitCard.id == card_id).first()
        
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Debit card with id {card_id} not found"
            )
        
        return {
            **card.__dict__,
            "account_name": card.savings_account.account_name,
            "bank_name": card.savings_account.bank_name,
            "current_balance": float(card.savings_account.current_balance)
        }
        
    @staticmethod
    def update_card(
        db: Session,
        card_id: int,
        card_data: DebitCardUpdate
    ) -> DebitCard:
        """Update debit card"""
        card = DebitCardService.get_card_by_id(db, card_id)
        
        update_data = card_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(card, field, value)
        
        db.commit()
        db.refresh(card)
        return card
    
    @staticmethod
    def delete_card(db: Session, card_id: int) -> None:
        """Delete debit card"""
        card = DebitCardService.get_card_by_id(db, card_id)
        db.delete(card)
        db.commit()
        
    @staticmethod
    def activate_card(db: Session, card_id: int) -> DebitCard:
        """Activate a debit card"""
        card = DebitCardService.get_card_by_id(db, card_id)
        card.is_active = True
        db.commit()
        db.refresh(card)
        return card
    
    @staticmethod
    def deactivate_card(db: Session, card_id: int) -> DebitCard:
        """Deactivate a debit card"""
        card = DebitCardService.get_card_by_id(db, card_id)
        card.is_active = False
        db.commit()
        db.refresh(card)
        return card