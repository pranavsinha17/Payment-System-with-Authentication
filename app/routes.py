from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4
from app.db import SessionLocal
from app.models.user import User
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.models.payment import Payment
from app.schemas import (
    UserCreate, UserOut, Token, SubscriptionPlanCreate, SubscriptionPlanOut,
    UserSubscriptionCreate, UserSubscriptionOut, PaymentCreate, PaymentOut
)
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from sqlalchemy import and_

# User router
user_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@user_router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        id=str(uuid4()),
        email=user.email,
        phone=user.phone,
        password_hash=hashed_password,
        is_active=True,
        registered_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@user_router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@user_router.get("/users", response_model=list[UserOut])
def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # In a real app, check if current_user is admin
    return db.query(User).all()

@user_router.put("/me/phone", response_model=UserOut)
def update_phone(new_phone: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.phone = new_phone
    db.commit()
    db.refresh(current_user)
    return current_user

# Subscription router
subscription_router = APIRouter()

@subscription_router.post("/subscription-plans", response_model=SubscriptionPlanOut)
def create_subscription_plan(plan: SubscriptionPlanCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # In a real app, check if current_user is admin
    new_plan = SubscriptionPlan(
        id=str(uuid4()),
        name=plan.name,
        price=plan.price,
        duration=plan.duration,
        product_ids=plan.product_ids
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

@subscription_router.post("/user-subscriptions", response_model=UserSubscriptionOut)
def create_user_subscription(subscription: UserSubscriptionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # In a real app, check if plan_id is valid and if user is eligible
    new_subscription = UserSubscription(
        id=str(uuid4()),
        user_id=current_user.id,
        plan_id=subscription.plan_id,
        start_date=subscription.start_date,
        end_date=subscription.end_date,
        is_active=subscription.is_active
    )
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription

@subscription_router.get("/me/active-subscription", response_model=UserSubscriptionOut)
def get_active_subscription(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get the user's active subscription
    subscription = db.query(UserSubscription).filter(
        and_(
            UserSubscription.user_id == current_user.id,
            UserSubscription.is_active == True,
            UserSubscription.end_date > datetime.utcnow()
        )
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return subscription

@subscription_router.get("/me/subscriptions", response_model=list[UserSubscriptionOut])
def get_subscription_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get all subscriptions for the current user, ordered by creation date
    subscriptions = db.query(UserSubscription).filter(
        UserSubscription.user_id == current_user.id
    ).order_by(UserSubscription.created_at.desc()).all()
    
    return subscriptions

@subscription_router.post("/payments", response_model=PaymentOut)
def create_payment(payment: PaymentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify that the subscription exists and belongs to the user
    subscription = db.query(UserSubscription).filter(
        and_(
            UserSubscription.id == payment.subscription_id,
            UserSubscription.user_id == current_user.id
        )
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found or does not belong to the user"
        )
    
    # In a real app, verify the payment with Razorpay
    new_payment = Payment(
        id=str(uuid4()),
        user_id=current_user.id,
        subscription_id=payment.subscription_id,
        razorpay_payment_id=payment.razorpay_payment_id,
        amount=payment.amount,
        status=payment.status,
        paid_at=payment.paid_at
    )
    db.add(new_payment)
    
    # Activate subscription only if payment is successful
    if payment.status.lower() == "completed":
        subscription.is_active = True
        # Update start_date to current time if it's a new subscription
        if subscription.start_date > datetime.utcnow():
            subscription.start_date = datetime.utcnow()
            # Recalculate end_date based on plan duration
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription.plan_id).first()
            if plan.duration == "monthly":
                subscription.end_date = subscription.start_date + timedelta(days=30)
            elif plan.duration == "quarterly":
                subscription.end_date = subscription.start_date + timedelta(days=90)
            elif plan.duration == "yearly":
                subscription.end_date = subscription.start_date + timedelta(days=365)
    
    db.commit()
    db.refresh(new_payment)
    return new_payment 