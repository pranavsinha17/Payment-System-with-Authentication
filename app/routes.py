from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File
from sqlalchemy.orm import Session
from uuid import uuid4
from app.db import SessionLocal
from app.models.user import User
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.models.payment import Payment
from app.models.product import Product
from app.models.product_selection import ProductSelection
from app.schemas import (
    UserCreate, UserOut, Token, SubscriptionPlanCreate, SubscriptionPlanOut,
    UserSubscriptionCreate, UserSubscriptionOut, PaymentCreate, PaymentOut,
    PlanChangeResponse, ProductSelectionBulkCreate, ProductSelectionBulkResponse,
    ProductSelectionOut, DetailedSubscriptionResponse, ProductCreate, ProductOut,
    CreateOrderRequest, CreateOrderResponse, LoginRequest,
    SuccessResponse, SuccessListResponse, MessageResponse
)
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user, require_role
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from sqlalchemy import and_
from typing import Optional, List
import json
import secrets
from pydantic import BaseModel
from app.utils.email_utils import send_email
import pandas as pd
from fastapi.responses import StreamingResponse
import io
from app.services.razorpay_service import razorpay_service
from app.config.razorpay import razorpay_settings
from app.exceptions import BadRequestException, NotFoundException, UnauthorizedException, ForbiddenException, ConflictException, UnprocessableEntityException

# User router
user_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@user_router.post("/register", response_model=SuccessResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check for duplicate email
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise BadRequestException("Email already registered")
    
    # Check for duplicate phone
    db_user_phone = db.query(User).filter(User.phone == user.phone).first()
    if db_user_phone:
        raise BadRequestException("Phone number already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        id=str(uuid4()),
        email=user.email,
        phone=user.phone,
        fullname=user.fullname,
        password_hash=hashed_password,
        is_active=True,
        registered_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"success": True, "data": UserOut.from_orm(new_user)}

@user_router.post("/login", response_model=SuccessResponse)
def login(request: LoginRequest, db: Session = Depends(get_db), response: Response = None):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise BadRequestException("Incorrect email or password")
    access_token = create_access_token(data={
        "sub": user.id,
        "last_password_change": str(user.last_password_change) if user.last_password_change else ""
    })
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="none",  # or "none" if using cross-site cookies with HTTPS
        secure=True      # set to True in production with HTTPS
    )
    return {"success": True, "data": {"access_token": access_token, "token_type": "bearer"}}

@user_router.get("/me", response_model=SuccessResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    print(current_user)
    return {"success": True, "data": UserOut.from_orm(current_user)}

@user_router.get("/admin/users", response_model=SuccessListResponse, dependencies=[Depends(require_role("admin"))])
def admin_list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"success": True, "data": [UserOut.from_orm(u) for u in users]}

@user_router.get("/users", response_model=SuccessListResponse)
def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"success": True, "data": [UserOut.from_orm(u) for u in users]}

@user_router.put("/me/phone", response_model=SuccessResponse)
def update_phone(new_phone: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.phone = new_phone
    db.commit()
    db.refresh(current_user)
    return {"success": True, "data": UserOut.from_orm(current_user)}

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@user_router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise NotFoundException("User with this email does not exist.")
    # Generate a secure token and expiry (1 hour)
    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(hours=1)
    user.password_reset_token = token
    user.password_reset_token_expiry = expiry
    db.commit()
    # Send the reset link via email
    reset_link = f"http://localhost:3000/reset-password?token={token}"
    email_body = f"Click the link to reset your password: <a href='{reset_link}'>{reset_link}</a>"
    send_email(
        subject="Password Reset Request",
        body=email_body,
        to_email=user.email
    )
    return {"success": True, "data": {"message": "If this email exists, a password reset link has been sent."}}

@user_router.post("/reset-password", response_model=MessageResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.password_reset_token == request.token).first()
    if not user or not user.password_reset_token_expiry or user.password_reset_token_expiry < datetime.utcnow():
        raise BadRequestException("Invalid or expired token.")
    user.password_hash = get_password_hash(request.new_password)
    user.password_reset_token = None
    user.password_reset_token_expiry = None
    user.last_password_change = datetime.utcnow()
    db.commit()
    return {"success": True, "data": {"message": "Password has been reset successfully."}}

@user_router.post("/logout", response_model=MessageResponse)
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"success": True, "data": {"message": "Logged out successfully."}}

# Subscription router
subscription_router = APIRouter()

@subscription_router.post("/subscription-plans", response_model=SuccessResponse)
def create_subscription_plan(
    plan: SubscriptionPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create new subscription plan
    new_plan = SubscriptionPlan(
        name=plan.name,
        price=plan.price,
        duration=plan.duration,
        product_ids=plan.product_ids  # This will be converted to JSON string in the model
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return {"success": True, "data": SubscriptionPlanOut.from_orm(new_plan)}

@subscription_router.post("/trial-plan", response_model=SuccessResponse)
def create_trial_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get all available products
    all_products = db.query(Product).all()
    product_ids = [product.id for product in all_products]
    
    # Create trial plan with all products
    trial_plan = SubscriptionPlan(
        name="30-Day Free Trial",
        price=0.0,  # Free trial
        duration="monthly",
        product_ids=product_ids
    )
    db.add(trial_plan)
    db.commit()
    db.refresh(trial_plan)
    return {"success": True, "data": SubscriptionPlanOut.from_orm(trial_plan)}

@subscription_router.post("/user-subscriptions", response_model=SuccessResponse)
def create_user_subscription(subscription: UserSubscriptionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if user already has an active subscription
    existing_subscription = db.query(UserSubscription).filter(
        and_(
            UserSubscription.user_id == current_user.id,
            UserSubscription.is_active == True,
            UserSubscription.end_date > datetime.utcnow()
        )
    ).first()
    
    if existing_subscription:
        raise BadRequestException(
            "You already have an active subscription. Please wait until it expires or cancel it first."
        )
    
    # Check if this is a first-time user who hasn't used their trial
    if not current_user.has_used_trial:
        # Find the trial plan
        trial_plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.name == "Trial Plan"
        ).first()
        
        if not trial_plan:
            raise NotFoundException(
                "Trial plan not found. Please contact support."
            )
        
        # Create a trial subscription
        new_subscription = UserSubscription(
            id=str(uuid4()),
            user_id=current_user.id,
            plan_id=trial_plan.id,  # Use trial plan ID
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),  # 30-day trial
            is_active=True  # Activate trial immediately
        )
        
        # Update user's has_used_trial field
        db.query(User).filter(User.id == current_user.id).update({"has_used_trial": True})
        
        db.add(new_subscription)
        db.commit()
        db.refresh(new_subscription)
        return {"success": True, "data": UserSubscriptionOut.from_orm(new_subscription)}
    else:
        # Regular subscription creation
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
        return {"success": True, "data": UserSubscriptionOut.from_orm(new_subscription)}

@subscription_router.get("/me/active-subscription", response_model=SuccessResponse)
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
        raise NotFoundException(
            "No active subscription found"
        )
    
    # Get the subscription plan
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription.plan_id).first()
    
    # Get all active product selections for this subscription with product details
    selections = db.query(ProductSelection).filter(
        and_(
            ProductSelection.subscription_id == subscription.id,
            ProductSelection.is_active == True,
            ProductSelection.user_id == current_user.id
        )
    ).all()
    
    # Get product details for each selection
    product_selections = []
    for selection in selections:
        product = db.query(Product).filter(Product.id == selection.product_id).first()
        if product:
            product_selections.append({
                "id": selection.id,
                "product_id": selection.product_id,
                "is_active": selection.is_active,
                "created_at": selection.created_at,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "type": product.type,
                    "script_ref": product.script_ref,
                    "output_type": product.output_type
                }
            })
    
    # Calculate total price based on number of selected products
    total_price = plan.price if not product_selections else plan.price * len(product_selections)
    
    # Create response dictionary
    response = {
        "id": subscription.id,
        "user_id": subscription.user_id,
        "plan_id": subscription.plan_id,
        "start_date": subscription.start_date,
        "end_date": subscription.end_date,
        "is_active": subscription.is_active,
        "created_at": subscription.created_at,
        "plan": plan,
        "product_selections": product_selections,
        "total_price": total_price,
        "number_of_products": len(product_selections)
    }
    
    response["plan"] = SubscriptionPlanOut.from_orm(response["plan"]) if response.get("plan") else None
    return {"success": True, "data": response}

@subscription_router.get("/me/subscriptions", response_model=SuccessListResponse)
def get_user_subscriptions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get all subscriptions for the user
    subscriptions = db.query(UserSubscription).filter(
        UserSubscription.user_id == current_user.id
    ).all()
    
    detailed_subscriptions = []
    for subscription in subscriptions:
        # Get the subscription plan
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription.plan_id).first()
        
        # First get the product selections without joining
        selections = db.query(ProductSelection).filter(
            and_(
                ProductSelection.subscription_id == subscription.id,
                ProductSelection.is_active == True,
                ProductSelection.user_id == current_user.id
            )
        ).all()
        
        # Then get the products for these selections
        product_selections = []
        for selection in selections:
            product = db.query(Product).filter(Product.id == selection.product_id).first()
            if product:
                product_selections.append({
                    "id": selection.id,
                    "product_id": selection.product_id,
                    "is_active": selection.is_active,
                    "created_at": selection.created_at,
                    "product": {
                        "id": product.id,
                        "name": product.name,
                        "description": product.description,
                        "type": product.type,
                        "script_ref": product.script_ref,
                        "output_type": product.output_type
                    }
                })
        
        # Calculate total price based on number of selected products
        # If no products are selected, use the base plan price
        total_price = plan.price if not product_selections else plan.price * len(product_selections)
        
        # Create detailed subscription response
        detailed_subscription = {
            "id": subscription.id,
            "user_id": subscription.user_id,
            "plan_id": subscription.plan_id,
            "start_date": subscription.start_date,
            "end_date": subscription.end_date,
            "is_active": subscription.is_active,
            "created_at": subscription.created_at,
            "plan": plan,
            "product_selections": product_selections,
            "total_price": total_price,
            "number_of_products": len(product_selections)
        }
        detailed_subscriptions.append(detailed_subscription)
    
    for ds in detailed_subscriptions:
        ds["plan"] = SubscriptionPlanOut.from_orm(ds["plan"]) if ds.get("plan") else None
    return {"success": True, "data": detailed_subscriptions}

@subscription_router.post("/create-order", response_model=SuccessResponse)
def create_payment_order(
    order_request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify that the subscription exists and belongs to the user
    subscription = db.query(UserSubscription).filter(
        and_(
            UserSubscription.id == order_request.subscription_id,
            UserSubscription.user_id == current_user.id
        )
    ).first()
    
    if not subscription:
        raise NotFoundException(
            "Subscription not found or does not belong to the user"
        )
    
    # Create Razorpay order
    order = razorpay_service.create_order(
        amount=order_request.amount,
        currency=order_request.currency,
        receipt=f"sub_{subscription.id}"
    )
    
    return {"success": True, "data": CreateOrderResponse(
        order_id=order["id"],
        amount=order_request.amount,
        currency=order_request.currency,
        key_id=razorpay_settings.RAZORPAY_KEY_ID
    )}

@subscription_router.post("/payments", response_model=SuccessResponse)
def create_payment(payment: PaymentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify that the subscription exists and belongs to the user
    subscription = db.query(UserSubscription).filter(
        and_(
            UserSubscription.id == payment.subscription_id,
            UserSubscription.user_id == current_user.id
        )
    ).first()
    
    if not subscription:
        raise NotFoundException(
            "Subscription not found or does not belong to the user"
        )
    
    # Verify the payment signature
    if not razorpay_service.verify_payment(
        payment_id=payment.razorpay_payment_id,
        order_id=payment.razorpay_order_id,
        signature=payment.razorpay_signature
    ):
        raise BadRequestException(
            "Invalid payment signature"
        )
    
    # Get payment details from Razorpay
    payment_details = razorpay_service.get_payment_details(payment.razorpay_payment_id)
    
    # Create payment record
    new_payment = Payment(
        id=str(uuid4()),
        user_id=current_user.id,
        subscription_id=payment.subscription_id,
        razorpay_payment_id=payment.razorpay_payment_id,
        razorpay_order_id=payment.razorpay_order_id,
        razorpay_signature=payment.razorpay_signature,
        amount=payment.amount,
        status=payment_details["status"],
        paid_at=datetime.fromtimestamp(payment_details["created_at"])
    )
    db.add(new_payment)
    
    # Activate subscription only if payment is successful
    if payment_details["status"] == "captured":
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
    return {"success": True, "data": PaymentOut.from_orm(new_payment)}

@subscription_router.post("/{subscription_id}/change-plan", response_model=SuccessResponse)
def change_subscription_plan(
    subscription_id: str,
    new_plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"Current User ID: {current_user.id}")
    print(f"Requested Subscription ID: {subscription_id}")
    print(f"New Plan ID: {new_plan_id}")
    
    # Get current subscription
    current_subscription = db.query(UserSubscription).filter(
        and_(
            UserSubscription.id == subscription_id,
            UserSubscription.user_id == current_user.id
        )
    ).first()
    
    if not current_subscription:
        print(f"No subscription found with ID: {subscription_id} for user: {current_user.id}")
        raise NotFoundException(
            "Subscription not found or does not belong to the user"
        )
    
    print(f"Found subscription: {current_subscription.id}")
    print(f"Current plan ID: {current_subscription.plan_id}")
    
    # Get new plan
    new_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == new_plan_id).first()
    if not new_plan:
        print(f"No plan found with ID: {new_plan_id}")
        raise NotFoundException(
            "New plan not found"
        )
    
    print(f"Found new plan: {new_plan.id}")
    
    # Get current plan
    current_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == current_subscription.plan_id
    ).first()
    
    # Calculate remaining days in current subscription
    remaining_days = (current_subscription.end_date - datetime.utcnow()).days
    if remaining_days < 0:
        remaining_days = 0
    
    print(f"Remaining days: {remaining_days}")
    
    # Calculate prorated amount
    daily_rate_current = current_plan.price / 30  # Assuming monthly plans
    daily_rate_new = new_plan.price / 30
    remaining_value = daily_rate_current * remaining_days
    new_value = daily_rate_new * remaining_days
    price_difference = new_value - remaining_value
    
    print(f"Price difference: {price_difference}")
    
    # Create new subscription
    new_subscription = UserSubscription(
        id=str(uuid4()),
        user_id=current_user.id,
        plan_id=new_plan_id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=remaining_days),
        is_active=False  # Will be activated after payment
    )
    
    # Deactivate current subscription
    current_subscription.is_active = False
    
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    
    print(f"Created new subscription: {new_subscription.id}")
    
    return {"success": True, "data": PlanChangeResponse(
        subscription=UserSubscriptionOut.from_orm(new_subscription),
        price_difference=price_difference,
        remaining_days=remaining_days
    )}

@subscription_router.get("/subscription-plans", response_model=SuccessListResponse)
def list_subscription_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available subscription plans"""
    plans = db.query(SubscriptionPlan).all()
    return {"success": True, "data": [SubscriptionPlanOut.from_orm(p) for p in plans]}

@subscription_router.post("/product-selections", response_model=SuccessResponse)
def create_product_selections(
    bulk_selection: ProductSelectionBulkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify subscription exists and belongs to user
    subscription = db.query(UserSubscription).filter(
        and_(
            UserSubscription.id == bulk_selection.subscription_id,
            UserSubscription.user_id == current_user.id
        )
    ).first()
    
    if not subscription:
        raise NotFoundException("Subscription not found")
    
    # Get the subscription plan
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription.plan_id).first()
    if not plan:
        raise NotFoundException("Subscription plan not found")
    
    # Verify all product IDs exist in the plan's product_ids
    plan_product_ids = json.loads(plan.product_ids) if isinstance(plan.product_ids, str) else plan.product_ids
    invalid_products = [pid for pid in bulk_selection.product_ids if pid not in plan_product_ids]
    if invalid_products:
        raise BadRequestException(
            f"Products {invalid_products} are not available in this plan"
        )
    
    # Deactivate any existing product selections for this subscription
    db.query(ProductSelection).filter(
        ProductSelection.subscription_id == subscription.id
    ).update({"is_active": False})
    
    # Create new product selections
    selections = []
    for product_id in bulk_selection.product_ids:
        selection = ProductSelection(
            user_id=current_user.id,
            subscription_id=subscription.id,
            product_id=product_id,
            is_active=True
        )
        db.add(selection)
        selections.append(selection)
    
    db.commit()
    
    # Refresh selections to get their IDs
    for selection in selections:
        db.refresh(selection)
    
    # Calculate total price based on number of products
    total_price = plan.price * len(bulk_selection.product_ids)
    
    return {"success": True, "data": {
        "selections": [ProductSelectionOut.from_orm(s) for s in selections],
        "total_price": total_price,
        "duration": plan.duration,
        "number_of_products": len(bulk_selection.product_ids)
    }}

@subscription_router.get("/subscriptions/{subscription_id}/product-selections", response_model=SuccessListResponse)
def get_product_selections(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify subscription exists and belongs to user
    subscription = db.query(UserSubscription).filter(
        and_(
            UserSubscription.id == subscription_id,
            UserSubscription.user_id == current_user.id
        )
    ).first()
    
    if not subscription:
        raise NotFoundException(
            "Subscription not found or does not belong to the user"
        )
    
    # Get all product selections for this subscription
    selections = db.query(ProductSelection).filter(
        ProductSelection.subscription_id == subscription_id
    ).all()
    
    return {"success": True, "data": [ProductSelectionOut.from_orm(s) for s in selections]}

@subscription_router.delete("/product-selections/{selection_id}", response_model=MessageResponse)
def delete_product_selection(
    selection_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify selection exists and belongs to user
    selection = db.query(ProductSelection).filter(
        and_(
            ProductSelection.id == selection_id,
            ProductSelection.user_id == current_user.id
        )
    ).first()
    
    if not selection:
        raise NotFoundException(
            "Product selection not found or does not belong to the user"
        )
    
    # Soft delete by setting is_active to False
    selection.is_active = False
    db.commit()
    
    return {"success": True, "data": {"message": "Product selection deactivated successfully"}}

@subscription_router.post("/products", response_model=SuccessResponse)
def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create new product
    new_product = Product(
        id=product.id,
        name=product.name,
        description=product.description,
        type=product.type,
        script_ref=product.script_ref,
        output_type=product.output_type
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"success": True, "data": ProductOut.from_orm(new_product)}

@subscription_router.post("/product1/process-file")
def process_product1_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check for active subscription (reuse your existing logic)
    subscription = db.query(UserSubscription).filter(
        and_(
            UserSubscription.user_id == current_user.id,
            UserSubscription.is_active == True,
            UserSubscription.end_date > datetime.utcnow()
        )
    ).first()
    if not subscription:
        raise ForbiddenException("Your subscription has expired. Please subscribe to continue.")

    # Read the uploaded file into a DataFrame
    if file.filename.endswith('.csv'):
        df = pd.read_csv(file.file)
    elif file.filename.endswith('.xls') or file.filename.endswith('.xlsx'):
        df = pd.read_excel(file.file)
    else:
        raise BadRequestException("Only CSV and Excel files are supported.")

    # --- Tweak the DataFrame here (example: add a column) ---
    df['tweaked'] = 'example tweak'  # Replace with your actual logic
    # -------------------------------------------------------

    # Write the tweaked DataFrame to an Excel file in-memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': f'attachment; filename="tweaked_{file.filename.rsplit('.', 1)[0]}.xlsx"'
        }
    ) 