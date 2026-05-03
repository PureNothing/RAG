from sqlalchemy.orm import mapped_column, Mapped
from app.auth.dbengine import Base
from sqlalchemy import String, DateTime, func
from typing import Annotated
import datetime

intpk = Annotated[int, mapped_column(primary_key=True)]
s_time = Annotated[datetime.datetime, mapped_column(DateTime(timezone=True), server_default=func.now())]

class Users(Base):
    __tablename__ = "Users"

    id: Mapped[intpk]
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[s_time]
