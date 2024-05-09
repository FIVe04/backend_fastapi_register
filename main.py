from contextlib import asynccontextmanager
from datetime import timedelta, datetime
from typing import Union
from jose import JWTError, jwt

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from database import create_tables, delete_tables
from schemas import UserCreate

from repository import UserRepository
from passlib.context import CryptContext

@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    await create_tables()
    print('created db')
    yield
    print("OFF")


app = FastAPI(lifespan=lifespan)

origins = [
    "http://192.168.1.65:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



@app.post("/api/users")
async def create_user(user: UserCreate):
    response = await UserRepository.get_user_by_username(user.email)
    if response is None:
        return await UserRepository.create_one(user)
    raise HTTPException(status_code=409, detail="User with this username already exists")

@app.get("/api/users")
async def get_users():
    users = await UserRepository.get_user()
    return users

@app.get("/api/users/{email}")
async def get_user(email: str):
    user = await UserRepository.get_user_by_username(email)
    return user


async def authenticate_user(email: str, password: str):
    user = await UserRepository.get_user_by_username(email)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    print(user)
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/api/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "email": user.email,"token_type": "bearer"}

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Token is invalid or expired")
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid or expired")

@app.get("/api/verify-token/{token}")
async def verify_user_token(token: str):
    verify_token(token)
    return {"message": "Token is valid"}


# TODO: Reorganize main - create routes.py
# TODO: Login with verification
# TODO: make prettier and easier to integrate


# @app.get("/")
# def read_root():
#     return {"id": 3}
#
#
# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id+3, "q": q}
#
# @app.post("/items/{item_id}")
# def create_item(item_id: int, q: Union[str, None] = None):
#     print(item_id)