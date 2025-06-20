from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from jose import jwt, JWTError
from app.models.user import User
from app.db import SessionLocal
from fastapi import status
from app.config.settings import SECRET_KEY, ALGORITHM

class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print("AuthenticationMiddleware called")
        # 1. Try to get token from cookie
        raw_token = request.cookies.get("access_token")
        # 2. If not found, try to get from Authorization header
        if not raw_token:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                raw_token = auth_header
        print("Raw token (cookie or header):", raw_token)
        user_info = None
        if raw_token and raw_token.startswith("Bearer "):
            raw_token = raw_token.split(" ", 1)[1]
        if raw_token:
            try:
                payload = jwt.decode(raw_token, SECRET_KEY, algorithms=[ALGORITHM])
                print("Decoded payload:", payload)
                user_id: str = payload.get("sub")
                token_last_password_change = payload.get("last_password_change")
                token_role = payload.get("role")
                print("user_id:", user_id)
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    print("User from DB:", user)
                    if user:
                        print("DB last_password_change:", user.last_password_change, "Token last_password_change:", token_last_password_change)
                    if user and token_last_password_change == str(user.last_password_change):
                        user_info = user  # Return the full User object
                finally:
                    db.close()
            except JWTError as e:
                print("JWTError:", e)
        else:
            print("No valid token found in cookie or header.")
        request.state.user_info = user_info
        response = await call_next(request)
        return response 