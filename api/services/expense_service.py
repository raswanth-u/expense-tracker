# api/services/expense_service.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract, and_, or_
from typing import Optional
from decimal import Decimal
from datetime import datetime, timezone

from db.models import (
    Expense, User, DebitCard, CreditCard, 
    SavingsAccount, SavingsTransaction, CreditCardTransaction
)
from api.schemas.expense import ExpenseCreate, ExpenseUpdate
from fastapi import HTTPException, status
from settings import setup_logging

logger = setup_logging("expense_service", "api.log")

class ExpenseService:
    """Service layer for expense operations"""
    
    @staticmethod
    def create_expense(db: Session, expense_data: ExpenseCreate) -> Expense:
        """Create a new expense with proper accounting"""
        logger.info(
            f"Creating expense: user_id={expense_data.user_id}, "
            f"amount=${expense_data.amount}, method={expense_data.payment_method}"
        )
        
        # Verify user exists
        user = db.query(User).filter(User.id == expense_data.user_id).first()
        if not user:
            logger.error(f"User not found: {expense_data.user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {expense_data.user_id} not found"
            )
        
        # Handle based on payment method
        if expense_data.payment_method.value == "debit_card":
            return ExpenseService._create_debit_card_expense(db, expense_data)
        
        elif expense_data.payment_method.value == "credit_card":
            return ExpenseService._create_credit_card_expense(db, expense_data)
        
        elif expense_data.payment_method.value in ["upi", "net_banking"]:
            return ExpenseService._create_upi_net_banking_expense(db, expense_data)
        
        else:
            # For cash, UPI, net_banking - simple expense record
            return ExpenseService._create_simple_expense(db, expense_data)
    
    @staticmethod
    def _create_debit_card_expense(db: Session, expense_data: ExpenseCreate) -> Expense:
        """Create expense paid with debit card (deducts from savings)"""
        logger.debug(f"Processing debit card expense: card_id={expense_data.debit_card_id}")
        
        # Verify debit card exists and belongs to user
        debit_card = db.query(DebitCard).options(
            joinedload(DebitCard.savings_account)
        ).filter(
            DebitCard.id == expense_data.debit_card_id,
            DebitCard.user_id == expense_data.user_id
        ).first()
        
        if not debit_card:
            logger.error(
                f"Debit card not found or doesn't belong to user: "
                f"card_id={expense_data.debit_card_id}, user_id={expense_data.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Debit card not found or doesn't belong to user"
            )
        
        savings_account = debit_card.savings_account
        
        # Check sufficient balance
        if savings_account.current_balance < expense_data.amount:
            logger.error(
                f"Insufficient balance: available=${savings_account.current_balance}, "
                f"required=${expense_data.amount}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Available: ${savings_account.current_balance}"
            )
        
        # Check minimum balance constraint
        new_balance = savings_account.current_balance - expense_data.amount
        # if new_balance < savings_account.minimum_balance:
        #     logger.error(
        #         f"Transaction would violate minimum balance: "
        #         f"new_balance=${new_balance}, minimum=${savings_account.minimum_balance}"
        #     )
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"Transaction would violate minimum balance of ${savings_account.minimum_balance}"
        #     )
        
        # Create savings transaction (withdrawal)
        savings_transaction = SavingsTransaction(
            # The above code is defining a variable `savings_account_id` in Python.
            savings_account_id=savings_account.id,
            transaction_type="debit_card",
            amount=expense_data.amount,
            balance_after=new_balance,
            transaction_date=expense_data.expense_date,
            description=f"Expense: {expense_data.category.value} - {expense_data.description or 'N/A'}"
        )
        
        # Update savings account balance
        savings_account.current_balance = new_balance
        
        # Create expense record
        expense = Expense(
            user_id=expense_data.user_id,
            debit_card_id=expense_data.debit_card_id,
            category=expense_data.category.value,
            amount=expense_data.amount,
            payment_method=expense_data.payment_method.value,
            expense_date=expense_data.expense_date,
            description=expense_data.description,
            merchant_name=expense_data.merchant_name,
            tags=expense_data.tags
        )
        
        db.add(savings_transaction)
        db.add(expense)
        db.flush()  # Get IDs
        
        # Link expense to savings transaction
        expense.savings_transaction_id = savings_transaction.id
        
        db.commit()
        db.refresh(expense)
        
        logger.info(
            f"Debit card expense created: ID={expense.id}, "
            f"new_balance=${new_balance}"
        )
        return expense
    
    @staticmethod
    def _create_credit_card_expense(db: Session, expense_data: ExpenseCreate) -> Expense:
        """Create expense paid with credit card"""
        logger.debug(f"Processing credit card expense: card_id={expense_data.credit_card_id}")
        
        # Verify credit card exists and belongs to user
        credit_card = db.query(CreditCard).filter(
            CreditCard.id == expense_data.credit_card_id,
            CreditCard.user_id == expense_data.user_id
        ).first()
        
        if not credit_card:
            logger.error(
                f"Credit card not found or doesn't belong to user: "
                f"card_id={expense_data.credit_card_id}, user_id={expense_data.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credit card not found or doesn't belong to user"
            )
        
        # Check available credit
        if credit_card.available_credit < expense_data.amount:
            logger.error(
                f"Insufficient credit: available=${credit_card.available_credit}, "
                f"required=${expense_data.amount}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient credit. Available: ${credit_card.available_credit}"
            )
        
        new_outstanding = credit_card.outstanding_balance + expense_data.amount
        new_available = credit_card.available_credit - expense_data.amount
        
        # Create credit card transaction
        cc_transaction = CreditCardTransaction(
            credit_card_id=credit_card.id,
            transaction_type="purchase",
            amount=expense_data.amount,
            transaction_date=expense_data.expense_date,
            outstanding_after=new_outstanding,
            description=f"{expense_data.category.value} - {expense_data.description or 'N/A'}",
            merchant_name=expense_data.merchant_name,
            tags=expense_data.tags
        )
        
        # Update credit card balances
        credit_card.outstanding_balance = new_outstanding
        credit_card.available_credit = new_available
        
        # Create expense record
        expense = Expense(
            user_id=expense_data.user_id,
            credit_card_id=expense_data.credit_card_id,
            category=expense_data.category.value,
            amount=expense_data.amount,
            payment_method=expense_data.payment_method.value,
            expense_date=expense_data.expense_date,
            description=expense_data.description,
            merchant_name=expense_data.merchant_name,
            tags=expense_data.tags
        )
        
        db.add(cc_transaction)
        db.add(expense)
        db.flush()
        
        # Link expense to credit card transaction
        expense.credit_card_transaction_id = cc_transaction.id
        
        db.commit()
        db.refresh(expense)
        
        logger.info(
            f"Credit card expense created: ID={expense.id}, "
            f"new_outstanding=${new_outstanding}"
        )
        return expense
    
    @staticmethod
    def _create_upi_net_banking_expense(db: Session, expense_data: ExpenseCreate) -> Expense:
        """Create expense paid with UPI or net banking (deducts from savings)"""
        logger.debug(f"Processing UPI/net_banking expense: account_id={expense_data.savings_account_id}")
        
        savings_account = db.query(SavingsAccount).filter(
            SavingsAccount.id == expense_data.savings_account_id,
            SavingsAccount.user_id == expense_data.user_id
        ).first()
        
        if not savings_account:
            logger.error(
                f"Savings account not found or doesn't belong to user: "
                f"account_id={expense_data.savings_account_id}, user_id={expense_data.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Savings account not found or doesn't belong to user"
            )
        
        # Check sufficient balance
        if savings_account.current_balance < expense_data.amount:
            logger.error(
                f"Insufficient balance: available=${savings_account.current_balance}, "
                f"required=${expense_data.amount}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Available: ${savings_account.current_balance}"
            )
        
        # Check minimum balance constraint
        new_balance = savings_account.current_balance - expense_data.amount
        # if new_balance < savings_account.minimum_balance:
        #     logger.error(
        #         f"Transaction would violate minimum balance: "
        #         f"new_balance=${new_balance}, minimum=${savings_account.minimum_balance}"
        #     )
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"Transaction would violate minimum balance of ${savings_account.minimum_balance}"
        #     )
        
        # Create savings transaction (withdrawal)
        savings_transaction = SavingsTransaction(
            # The above code is defining a variable `savings_account_id` in Python.
            savings_account_id=savings_account.id,
            transaction_type="upi" if expense_data.payment_method.value == "upi" else "net_banking",
            amount=expense_data.amount,
            balance_after=new_balance,
            transaction_date=expense_data.expense_date,
            description=f"Expense: {expense_data.category.value} - {expense_data.description or 'N/A'}"
        )
        
        # Update savings account balance
        savings_account.current_balance = new_balance
        
        # Create expense record
        expense = Expense(
            user_id=expense_data.user_id,
            savings_account_id=expense_data.savings_account_id,
            category=expense_data.category.value,
            amount=expense_data.amount,
            payment_method=expense_data.payment_method.value,
            expense_date=expense_data.expense_date,
            description=expense_data.description,
            merchant_name=expense_data.merchant_name,
            tags=expense_data.tags
        )
        
        db.add(expense)
        db.add(savings_transaction)
        db.flush()  # Get IDs
        db.commit()
        db.refresh(expense)
        
        logger.info(f"UPI/net_banking expense created: ID={expense.id}")
        return expense
    
    @staticmethod
    def _create_simple_expense(db: Session, expense_data: ExpenseCreate) -> Expense:
        """Create simple expense for cash payments"""
        logger.debug(f"Processing simple expense: method={expense_data.payment_method}")
        
        expense = Expense(
            user_id=expense_data.user_id,
            category=expense_data.category.value,
            amount=expense_data.amount,
            payment_method=expense_data.payment_method.value,
            expense_date=expense_data.expense_date,
            description=expense_data.description,
            merchant_name=expense_data.merchant_name,
            tags=expense_data.tags
        )
        
        db.add(expense)
        db.commit()
        db.refresh(expense)
        
        logger.info(f"Simple expense created: ID={expense.id}")
        return expense
    
    @staticmethod
    def get_expense_by_id(db: Session, expense_id: int) -> Expense:
        """Get expense by ID"""
        logger.debug(f"Fetching expense: {expense_id}")
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            logger.error(f"Expense not found: {expense_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expense with id {expense_id} not found"
            )
        return expense
    
    @staticmethod
    def get_expense_with_details(db: Session, expense_id: int) -> dict:
        """Get expense with card/account details"""
        expense = db.query(Expense).options(
            joinedload(Expense.debit_card).joinedload(DebitCard.savings_account),
            joinedload(Expense.credit_card),
            joinedload(Expense.savings_account)
        ).filter(Expense.id == expense_id).first()
        
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expense with id {expense_id} not found"
            )
        
        result = {**expense.__dict__}
        
        if expense.debit_card:
            result["card_name"] = expense.debit_card.card_name
            result["account_name"] = expense.debit_card.savings_account.account_name
            result["bank_name"] = expense.debit_card.savings_account.bank_name
        elif expense.credit_card:
            result["card_name"] = expense.credit_card.card_name
        elif expense.savings_account:
            result["account_name"] = expense.savings_account.account_name
            result["bank_name"] = expense.savings_account.bank_name
        
        return result
    
    @staticmethod
    def get_expenses(
        db: Session,
        user_id: Optional[int] = None,
        category: Optional[str] = None,
        payment_method: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[Expense], int]:
        """Get expenses with filters"""
        logger.debug(
            f"Fetching expenses: user_id={user_id}, category={category}, "
            f"method={payment_method}, date_range={start_date} to {end_date}"
        )
        
        query = db.query(Expense)
        
        if user_id:
            query = query.filter(Expense.user_id == user_id)
        
        if category:
            query = query.filter(Expense.category == category)
        
        if payment_method:
            query = query.filter(Expense.payment_method == payment_method)
        
        if start_date:
            query = query.filter(Expense.expense_date >= start_date)
        
        if end_date:
            query = query.filter(Expense.expense_date <= end_date)
        
        if min_amount:
            query = query.filter(Expense.amount >= min_amount)
        
        if max_amount:
            query = query.filter(Expense.amount <= max_amount)
        
        # Order by expense_date descending
        query = query.order_by(Expense.expense_date.desc())
        
        total = query.count()
        expenses = query.offset(skip).limit(limit).all()
        
        logger.info(f"Found {total} expenses")
        return expenses, total
    
    @staticmethod
    def update_expense(
        db: Session,
        expense_id: int,
        expense_data: ExpenseUpdate
    ) -> Expense:
        """Update expense (limited fields)"""
        logger.info(f"Updating expense: {expense_id}")
        expense = ExpenseService.get_expense_by_id(db, expense_id)
        
        update_data = expense_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(expense, field, value)
        
        db.commit()
        db.refresh(expense)
        logger.info(f"Expense updated: {expense_id}")
        return expense
    
    @staticmethod
    def delete_expense(db: Session, expense_id: int) -> None:
        """Delete expense (WARNING: This doesn't reverse transactions)"""
        logger.warning(f"Deleting expense: {expense_id}")
        expense = ExpenseService.get_expense_by_id(db, expense_id)
        
        # Log warning if expense had financial transaction
        if expense.savings_transaction_id or expense.credit_card_transaction_id:
            logger.warning(
                f"Deleting expense with linked transactions: "
                f"savings_txn={expense.savings_transaction_id}, "
                f"cc_txn={expense.credit_card_transaction_id}"
            )
        
        db.delete(expense)
        db.commit()
        logger.info(f"Expense deleted: {expense_id}")
    
    @staticmethod
    def get_statistics(
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get expense statistics"""
        logger.debug(f"Calculating statistics for user: {user_id}")
        
        query = db.query(Expense).filter(Expense.user_id == user_id)
        
        if start_date:
            query = query.filter(Expense.expense_date >= start_date)
        if end_date:
            query = query.filter(Expense.expense_date <= end_date)
        
        expenses = query.all()
        
        if not expenses:
            return {
                "total_expenses": 0,
                "total_amount": Decimal("0.00"),
                "by_category": {},
                "by_payment_method": {},
                "average_expense": Decimal("0.00"),
                "date_range": {}
            }
        
        # Calculate statistics
        total_amount = sum(e.amount for e in expenses)
        
        # Group by category
        by_category = {}
        for expense in expenses:
            category = expense.category
            by_category[category] = by_category.get(category, Decimal("0.00")) + expense.amount
        
        # Group by payment method
        by_payment_method = {}
        for expense in expenses:
            method = expense.payment_method
            by_payment_method[method] = by_payment_method.get(method, Decimal("0.00")) + expense.amount
        
        # Date range
        dates = [e.expense_date for e in expenses]
        date_range = {
            "start": min(dates),
            "end": max(dates)
        }
        
        logger.info(
            f"Statistics calculated: {len(expenses)} expenses, "
            f"total=${total_amount}"
        )
        
        return {
            "total_expenses": len(expenses),
            "total_amount": total_amount,
            "by_category": {k: float(v) for k, v in by_category.items()},
            "by_payment_method": {k: float(v) for k, v in by_payment_method.items()},
            "average_expense": total_amount / len(expenses),
            "date_range": date_range
        }
    
    @staticmethod
    def get_monthly_summary(
        db: Session,
        user_id: int,
        year: int,
        month: int
    ) -> dict:
        """Get monthly expense summary"""
        logger.debug(f"Getting monthly summary: user={user_id}, {year}-{month:02d}")
        
        expenses = db.query(Expense).filter(
            Expense.user_id == user_id,
            extract('year', Expense.expense_date) == year,
            extract('month', Expense.expense_date) == month
        ).all()
        
        if not expenses:
            return {
                "period": f"{year}-{month:02d}",
                "total_amount": Decimal("0.00"),
                "expense_count": 0,
                "top_category": None,
                "top_merchant": None
            }
        
        total_amount = sum(e.amount for e in expenses)
        
        # Find top category
        category_totals = {}
        for expense in expenses:
            cat = expense.category
            category_totals[cat] = category_totals.get(cat, Decimal("0.00")) + expense.amount
        top_category = max(category_totals.items(), key=lambda x: x[1])[0] if category_totals else None
        
        # Find top merchant
        merchant_totals = {}
        for expense in expenses:
            if expense.merchant_name:
                merchant = expense.merchant_name
                merchant_totals[merchant] = merchant_totals.get(merchant, Decimal("0.00")) + expense.amount
        top_merchant = max(merchant_totals.items(), key=lambda x: x[1])[0] if merchant_totals else None
        
        return {
            "period": f"{year}-{month:02d}",
            "total_amount": total_amount,
            "expense_count": len(expenses),
            "top_category": top_category,
            "top_merchant": top_merchant
        }