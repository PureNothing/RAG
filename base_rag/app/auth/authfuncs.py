from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from app.auth.config import SECRET_TOKEN

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()

class UserFuncs:

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_token(user_id: int) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        }
        return jwt.encode(payload, SECRET_TOKEN, algorithm="HS256")
    
    @staticmethod
    def decode_token(token: str) -> dict:
        return jwt.decode(token, SECRET_TOKEN, algorithms=["HS256"])
    
    @staticmethod
    def get_current_user(credentials = Depends(security)) -> int:
        try:
            payload = UserFuncs.decode_token(credentials.credentials)
            return payload["user_id"]
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Неверный или истекший токен. {e}")