from contextlib import asynccontextmanager
from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_tables, delete_tables
from schemas import UserCreate

from repository import UserRepository

@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    await create_tables()
    print('created db')
    yield
    print("OFF")


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/users")
async def create_user(user: UserCreate):
    return await UserRepository.create_one(user)

@app.get("/api/users")
async def get_users():
    users = await UserRepository.get_user()
    return users

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