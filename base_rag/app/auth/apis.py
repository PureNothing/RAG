from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.auth.dbfuncs import BDfuncs
from app.logger import logger
from app.auth.apischemas import UserLogin, UserRegister

@asynccontextmanager
async def lifespawn(router):
    logger.debug("Удаляю и поднимаю БД, запускаю API")
    try:
        await BDfuncs.create_tables()
        logger.info("БД успено пересоздана")
        yield
    except Exception as e:
        logger.error(f"Ошибка при пересоздании БД.")
        raise

router = APIRouter(lifespan=lifespawn)

@router.post("/auth/register")
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

@router.post("/auth/login")
async def user_login(message: UserLogin):
    logger.debug(f"Пришел запрос за вход пользоваетеля: {message.username}.")
    try:
        logger.debug("Иду в БД за создание токена и логинингом..")
        token = await BDfuncs.login_user(username=message.username, password=message.password)
        logger.info("Выдаю токен пользователю успешно!")
        return JSONResponse(status_code=201, content={"access_token": token, "token_type": "bearer"})
    except Exception as e:
        logger.error(f"Не удалось выдать токен или залогинить пользователя. {e}")
        raise HTTPException(status_code=500, detail=f"Не удалось залогинить пользователя или выдать токен. {e}")


