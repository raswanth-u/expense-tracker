# api/services/user_service.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from db.models import User, SavingsAccount, DebitCard, CreditCard, Expense
from api.schemas.user import UserCreate, UserUpdate
from fastapi import HTTPException, status

class UserService:
    """Service layer for user-related business logic"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        # check if name already exists
        existing_name = db.query(User).filter(User.name == user_data.name).first()
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User Name Taken"
            )
        
        # Create User
        user = User(
            name = user_data.name,
            email = user_data.email,
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """ Get User by ID """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Not Found"
            )
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, user_email: str) -> User:
        """ Get User by Email """
        user = db.query(User).filter(User.email == user_email).first()
        if not  user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Not Found"
            )
        return user
    
    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> tuple[list[User], int]:
        """Get list of users with pagination"""
        query = db.query(User)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
            
        total = query.count()
        
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        user_data: UserUpdate
    ) -> User:
        """ Update user Details """
        user = UserService.get_user_by_id(db, user_id)
        
        # update only provided data
        update_data = user_data.model_dump(exclude_unset=True)
        
        # check email
        if "email" in update_data and update_data["email"] != user.email: 
            existing_email = db.query(User).filter(User.email == update_data["email"]).first()
            if existing_email:
                raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="email already registered"
                    )
        # check user name
        if "name" in update_data and update_data["name"] != user.name:
            existing_name = db.query(User).filter(User.name == update_data["name"]).first()
            if existing_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=" user name taken "
                )
        
        # Apply Updates
        for field, value in update_data.items():
            setattr(user, field, value)
            
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(
        db: Session,
        user_id: int
    ) -> None:
        user = UserService.get_user_by_id(db, user_id)
        db.delete(user)
        db.commit()
        
    @staticmethod
    def get_user_summary(db: Session, user_id: int) -> dict:
        """ Get user with financial summary """
        user =  UserService.get_user_by_id(db, user_id)
        # print("Get User Summary called")
        # return { **user.__dict__}
        
        # Count related records
        total_savings_accounts = db.query(func.count(SavingsAccount.id)).filter(SavingsAccount.user_id == user_id).scalar()
        total_debit_cards = db.query(func.count(DebitCard.id)).filter(DebitCard.user_id == user_id).scalar()
        total_credit_cards = db.query(func.count(CreditCard.id)).filter(CreditCard.user_id == user_id).scalar()
        total_expenses = db.query(func.count(Expense.id)).filter(Expense.user_id == user_id).scalar()
        total_balance = db.query(func.sum(SavingsAccount.current_balance)).filter(SavingsAccount.user_id == user_id).scalar() or 0.0
        return {
            **user.__dict__,
            "total_savings_accounts": total_savings_accounts,
            "total_debit_cards": total_debit_cards,
            "total_credit_cards": total_credit_cards,
            "total_expenses": total_expenses,
            "total_balance": float(total_balance)
        }
            