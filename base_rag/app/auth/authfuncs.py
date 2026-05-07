from jose import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from app.auth.config import settings

security = HTTPBearer()

class UserFuncs:

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    
    @staticmethod
    def create_token(user_id: int) -> str:
        payload = {
            "type": "access",
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        }
        return jwt.encode(payload, settings.SECRET_TOKEN, algorithm="HS256")
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        payload = {
            "type": "refresh",
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(days=7)
        }
        return jwt.encode(payload, settings.SECRET_TOKEN, algorithm="HS256")
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        try:
            refresh_token = UserFuncs.decode_token(token=refresh_token)
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Ошибка при создании токена - {e}")
        if refresh_token["type"] == "refresh":
            new_token = UserFuncs.create_token(refresh_token["user_id"])
            return new_token
        else:
            raise HTTPException(status_code=401, detail=f"Токен не refresh.")
    
    @staticmethod
    def decode_token(token: str) -> dict:
        return jwt.decode(token, settings.SECRET_TOKEN, algorithms=["HS256"])
    
    @staticmethod
    def get_current_user(credentials = Depends(security)) -> int:
        try:
            payload = UserFuncs.decode_token(token=credentials.credentials)
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Неверный или истекший токен. {e}")
        if payload["type"] == "access":
            return payload["user_id"]
        else:
            raise HTTPException(status_code=401, detail="Это не access токен, вход запрещен.")