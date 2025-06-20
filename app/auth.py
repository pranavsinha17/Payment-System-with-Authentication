from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.db import SessionLocal
import logging

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger("auth")
logging.basicConfig(level=logging.INFO)  # You can adjust the level as needed

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # If a User object is provided, include more user details in the claims
    user = to_encode.get('user')
    if user:
        to_encode['sub'] = user.id
        to_encode['email'] = user.email
        to_encode['phone'] = user.phone
        to_encode['fullname'] = user.fullname
        to_encode['is_active'] = user.is_active
        to_encode['registered_at'] = str(user.registered_at) if user.registered_at else None
        to_encode['has_used_trial'] = user.has_used_trial
        to_encode['role'] = user.role
        to_encode['last_password_change'] = str(user.last_password_change) if user.last_password_change else None
    else:
        # Ensure 'role' and 'last_password_change' are included if not using a User object
        if 'role' not in to_encode:
            to_encode['role'] = 'user'
        if 'last_password_change' not in to_encode:
            to_encode['last_password_change'] = ''
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(request: Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Fetch token only from cookie
    raw_token = request.cookies.get("access_token")
    if raw_token and raw_token.startswith("Bearer "):
        raw_token = raw_token.split(" ", 1)[1]
    if not raw_token:
        raise credentials_exception
    try:
        payload = jwt.decode(raw_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_last_password_change = payload.get("last_password_change")
        token_role = payload.get("role")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    # Check last_password_change
    if token_last_password_change != str(user.last_password_change):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is no longer valid. Please log in again."
        )
    # Attach role from token to user object for downstream use
    user.role = token_role or user.role
    return user

def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker 