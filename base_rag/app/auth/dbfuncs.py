from sqlalchemy import select, insert
from app.auth.dbmodels import Users
from app.auth.authfuncs import UserFuncs
from app.auth.dbengine import async_session, engine, Base
from app.logger import logger


class BDfuncs:

    @staticmethod
    async def create_tables():
        async with engine.begin() as conn:
            logger.debug("Создаю таблицу и удаляю старую..")
            try:
                await conn.run_sync(Base.metadata.drop_all)
                logger.debug("Все таблицы удалены успешно.")
                await conn.run_sync(Base.metadata.create_all)
                logger.debug("Все таблицы успешно созданы.")
            except Exception as e:
                logger.error(f"Не удалось удалить или создать таблицы. {e}")
                raise

    @staticmethod
    async def register_user(username, password):
        logger.debug("Запрос на регистрацию пользователя в БД.")
        async with async_session() as session:
            try:
                logger.debug("Проверяю есть ли уже такой пользователь..")
                stmt = select(Users.username).where(Users.username == username)
                response = await session.execute(statement = stmt)
                result = response.scalar_one_or_none()
                if result:
                    logger.info("Пользователь уже существует.")
                    raise ValueError("Пользователь уже существует.")
                    
                stmt = insert(Users).values(
                    username = username,
                    hashed_password = UserFuncs.hash_password(password)
                )

                response = await session.execute(statement = stmt)
                logger.info(f"Пользователь {username} успешно зарегестрирован.")
                await session.commit()

            except Exception as e:
                logger.error(f"Не удалось зарегистрировать пользователя. {e}")
                await session.rollback()
                raise

        
    @staticmethod
    async def login_user(username: str, password: str) -> str:
        logger.info("Кто-то пытается войти в систему.")
        async with async_session() as session:
            try:

                stmt = select(Users).where(Users.username == username)
                response = await session.execute(statement=stmt)
                result = response.scalar_one_or_none()

                if not result or not UserFuncs.verify_password(password, result.hashed_password):
                    logger.info("Не верное имя пользователя или пароль.")
                    raise ValueError("Не верное имя пользователя или пароль.")
                
                logger.info("Вход успешный, выдаю токен.")
                return UserFuncs.create_token(result.id)
            except Exception as e:
                logger.error(f"Не удалось залогинить пользователя или выдать токен. {e}")
                await session.rollback()
                raise
