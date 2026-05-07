from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.auth.dbfuncs import BDfuncs
from app.auth.authfuncs import UserFuncs
from app.logger import logger
from app.auth.apischemas import UserLogin, UserRegister, TokenResponse, RefreshToken

router = APIRouter()

@router.post("/auth/register", )
async def user_register(message: UserRegister):
    logger.debug(f"Получен запрос на регитрацию: {message.username}.")
    try:
        logger.debug("Иду в БД за регистрацией..")
        await BDfuncs.register_user(username=message.username, password=message.password)
        logger.info(f"Регистрация прошла успешно! Для: {message.username}")
        return JSONResponse(status_code=201, content={"message": "Регистрация прошла успешно!"})
    except Exception as e:
        logger.error(f"Не удалось зарегистировать пользователя: {e}")
        raise HTTPException(status_code=500, detail=f"Не удалось зарегестрировать пользователя: {e}")

@router.post("/auth/login", response_model=TokenResponse)
async def user_login(message: UserLogin):
    logger.debug(f"Пришел запрос за вход пользоваетеля: {message.username}.")
    try:
        logger.debug("Иду в БД за создание токена и логинингом..")
        tokens = await BDfuncs.login_user(username=message.username, password=message.password)
        logger.info("Выдаю токен пользователю успешно!")
        return JSONResponse(status_code=201, content={"access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"], "token_type": "bearer"})
    except Exception as e:
        logger.error(f"Не удалось выдать токен или залогинить пользователя. {e}")
        raise HTTPException(status_code=500, detail=f"Не удалось залогинить пользователя или выдать токен. {e}")
    
@router.post("/auth/refresh_token")
async def refresh_token(refresh_token: RefreshToken) -> str:
    logger.debug(f"Пришел запрос на обновления access токена через refresh_token")
    try:
        new_access_token = UserFuncs.refresh_access_token(refresh_token=refresh_token.refresh_token)
        return {"access_token": new_access_token}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Не удалось выдать новый access через refresh. {e}")
        raise HTTPException(status_code=401, detail=f"Не удалось выдать новый access через refresh. {e}")


