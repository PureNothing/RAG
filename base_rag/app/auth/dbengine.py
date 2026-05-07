from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.auth.config import settings

engine = create_async_engine(
    url=settings.POSTGRES_URL,
    echo=False,
    pool_size = 5,
    max_overflow = 10
)

async_session = async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass

