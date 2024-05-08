import datetime as _dt
from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    email: str
    hashed_password: str

class User(UserCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


