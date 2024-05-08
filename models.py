from typing import Optional

import sqlalchemy as _sql
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

import passlib.hash as _hash




class Model(DeclarativeBase):
    pass


class UserOrm(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]

    # def verify_password(self, password: str):
    #     return _hash.bcrypt.verify(password, self.hashed_password)

