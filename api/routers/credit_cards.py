# api/routers/credit_cards.py
from fastapi import APIRouter, Depends, Query, status, Path
from sqlalchemy.orm import Session
from typing import Optional

from api.dependencies import get_db, verify_api_key
from api.schemas.credit_card import (
    CreditCardCreate, CreditCardUpdate, CreditCardResponse, CreditCardListResponse,
    CreditCardTransactionCreate, CreditCardTransactionResponse, CreditCardTransactionListResponse,
    CreditCardPaymentCreate, CreditCardPaymentResponse, CreditCardPaymentListResponse
)
from api.services.credit_card_service import CreditCardService
from settings import setup_logging

logger = setup_logging("credit_card_router", "api.log")

router = APIRouter(
    prefix="/credit-cards",
    tags=["credit-cards"],
    dependencies=[Depends(verify_api_key)],
)

@router.post(
    "/",
    response_model=CreditCardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create credit card"
)
def create_card(
    card: CreditCardCreate,
    db: Session = Depends(get_db)
) -> CreditCardResponse:
    """Create a new credit card"""
    logger.info(f"API: Creating credit card for user {card.user_id}")
    result = CreditCardService.create_card(db, card)
    logger.info(f"API: Credit card created with ID {result.id}")
    return result

@router.get(
    "/",
    response_model=CreditCardListResponse,
    summary="List credit cards"
)
def get_cards(
    user_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> CreditCardListResponse:
    """Get list of credit cards"""
    logger.debug(f"API: Listing credit cards (user_id={user_id})")
    cards, total = CreditCardService.get_cards(db, user_id, is_active, skip, limit)
    return CreditCardListResponse(total=total, cards=cards)

@router.get(
    "/{card_id}",
    response_model=CreditCardResponse,
    summary="Get credit card"
)
def get_card(
    card_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
) -> CreditCardResponse:
    """Get credit card by ID"""
    logger.debug(f"API: Fetching credit card {card_id}")
    return CreditCardService.get_card_by_id(db, card_id)

@router.put(
    "/{card_id}",
    response_model=CreditCardResponse,
    summary="Update credit card"
)
def update_card(
    card_id: int = Path(..., gt=0),
    card_data: CreditCardUpdate = ...,
    db: Session = Depends(get_db)
) -> CreditCardResponse:
    """Update credit card"""
    logger.info(f"API: Updating credit card {card_id}")
    return CreditCardService.update_card(db, card_id, card_data)

@router.delete(
    "/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete credit card"
)
def delete_card(
    card_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
) -> None:
    """Delete credit card"""
    logger.warning(f"API: Deleting credit card {card_id}")
    CreditCardService.delete_card(db, card_id)

# Transaction endpoints
@router.post(
    "/transactions",
    response_model=CreditCardTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create transaction"
)
def create_transaction(
    transaction: CreditCardTransactionCreate,
    db: Session = Depends(get_db)
) -> CreditCardTransactionResponse:
    """Create a credit card transaction (purchase, refund, fee, etc.)"""
    logger.info(f"API: Creating transaction for card {transaction.credit_card_id}")
    return CreditCardService.create_transaction(db, transaction)

@router.get(
    "/{card_id}/transactions",
    response_model=CreditCardTransactionListResponse,
    summary="Get card transactions"
)
def get_transactions(
    card_id: int = Path(..., gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> CreditCardTransactionListResponse:
    """Get transactions for a card"""
    logger.debug(f"API: Fetching transactions for card {card_id}")
    transactions, total = CreditCardService.get_transactions(db, card_id, skip, limit)
    return CreditCardTransactionListResponse(total=total, transactions=transactions)

# Payment endpoints
@router.post(
    "/payments",
    response_model=CreditCardPaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Make payment"
)
def create_payment(
    payment: CreditCardPaymentCreate,
    db: Session = Depends(get_db)
) -> CreditCardPaymentResponse:
    """Make a payment from savings account to credit card"""
    logger.info(f"API: Processing payment for card {payment.credit_card_id}")
    return CreditCardService.create_payment(db, payment)

@router.get(
    "/{card_id}/payments",
    response_model=CreditCardPaymentListResponse,
    summary="Get card payments"
)
def get_payments(
    card_id: int = Path(..., gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> CreditCardPaymentListResponse:
    """Get payments for a card"""
    logger.debug(f"API: Fetching payments for card {card_id}")
    payments, total = CreditCardService.get_payments(db, card_id, skip, limit)
    return CreditCardPaymentListResponse(total=total, payments=payments)