from sqlalchemy import select

from database import new_session
from models import UserOrm
from schemas import UserCreate, User
import passlib.hash as _hash

class UserRepository:
    @classmethod
    async def create_one(cls, data: UserCreate) -> int:
        async with new_session() as session:
            user_dict = data.model_dump()
            user_dict["hashed_password"] = _hash.bcrypt.hash(user_dict["hashed_password"])
            user = UserOrm(**user_dict)
            session.add(user)
            await session.flush()
            await session.commit()
            return user.id

    @classmethod
    async def get_user(cls):
        async with new_session() as session:
            query = select(UserOrm)
            result = await session.execute(query)
            user_models = result.scalars().all()
            # user_schemas = [User.model_validate(user_model) for user_model in user_models]
            return user_models

    @classmethod
    async def get_user_by_username(cls, email: str):
        async with new_session() as session:
            response = await session.execute(select(UserOrm).filter(UserOrm.email == email))
            user_model = response.scalars().first()
            return user_model
