# api/routers/debit_cards.py
from fastapi import APIRouter, Depends, Query, status, Path
from sqlalchemy.orm import Session
from typing import Optional

from api.dependencies import get_db, verify_api_key
from api.schemas.debit_card import (
    DebitCardCreate,
    DebitCardUpdate,
    DebitCardResponse,
    DebitCardWithDetails,
    DebitCardListResponse
)
from api.services.debit_card_service import DebitCardService

router = APIRouter(
    prefix="/debit-cards",
    tags=["debit-cards"],
    dependencies=[Depends(verify_api_key)],
)

@router.post(
    "/",
    response_model=DebitCardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create debit card"
)
def create_card(
    card: DebitCardCreate,
    db: Session = Depends(get_db)
) -> DebitCardResponse:
    """
    Create a new debit card linked to a savings account.
    
    - Card must be linked to existing user and savings account
    - Card number must be unique
    - Card type must be: visa, mastercard, or rupay
    """
    return DebitCardService.create_card(db, card)

@router.get(
    "/",
    response_model=DebitCardListResponse,
    summary="List debit cards"
)
def get_cards(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> DebitCardListResponse:
    """Get list of debit cards with optional filters"""
    cards, total = DebitCardService.get_cards(db, user_id, is_active, skip, limit)
    return DebitCardListResponse(total=total, cards=cards)

@router.get(
    "/{card_id}",
    response_model=DebitCardResponse,
    summary="Get debit card"
)
def get_card(
    card_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
) -> DebitCardResponse:
    """Get debit card by ID"""
    return DebitCardService.get_card_by_id(db, card_id)

@router.get(
    "/{card_id}/details",
    response_model=DebitCardWithDetails,
    summary="Get debit card with account details"
)
def get_card_with_details(
    card_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
) -> DebitCardWithDetails:
    """Get debit card with associated savings account information"""
    return DebitCardService.get_card_with_details(db, card_id)

@router.put(
    "/{card_id}",
    response_model=DebitCardResponse,
    summary="Update debit card"
)
def update_card(
    card_id: int = Path(..., gt=0),
    card_data: DebitCardUpdate = ...,
    db: Session = Depends(get_db)
) -> DebitCardResponse:
    """Update debit card details"""
    return DebitCardService.update_card(db, card_id, card_data)

@router.delete(
    "/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete debit card"
)
def delete_card(
    card_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
) -> None:
    """Delete debit card"""
    DebitCardService.delete_card(db, card_id)
    
@router.post(
    "/{card_id}/activate",
    response_model=DebitCardResponse,
    summary="Activate debit card"
)
def activate_card(
    card_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
) -> DebitCardResponse:
    """Activate a debit card"""
    return DebitCardService.activate_card(db, card_id)

@router.post(
    "/{card_id}/deactivate",
    response_model=DebitCardResponse,
    summary="Deactivate debit card"
)
def deactivate_card(
    card_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
) -> DebitCardResponse:
    """Deactivate a debit card"""
    return DebitCardService.deactivate_card(db, card_id)