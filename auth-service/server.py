import os
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from databases import Database
from sqlalchemy import Column, Integer, String, create_engine, MetaData, Table
from sqlalchemy.sql import select
from pydantic import BaseModel

# Configure FastAPI app
app = FastAPI()

# Secret key to sign JWT tokens i(should be kept secret)
SECRET_KEY = "hefni-key"

# Algorithm to use for JWT token signing
ALGORITHM = "HS256"

# Token expiration time (in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DB_URI = os.getenv("DB_URI")
DATABASE_URL = f"sqlite:///{DB_URI}"

# SQLAlchemy database engine and connection
engine = create_engine(DATABASE_URL)
metadata = MetaData()


# Define the "users" table
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("username", String, unique=True, index=True),
    Column("password", String),
)

# Initialize the database
database = Database(DATABASE_URL)

# Initialize the database tables
metadata.create_all(engine)

class UserRegistration(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str



# User model for authentication
class UserBase:
    def __init__(self, username: str):
        self.username = username

# User model to return in response
class User(UserBase):
    def __init__(self, username: str, role: str = "user"):
        super().__init__(username)
        self.role = role

# JWT token creation function
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# JWT token verification function
def verify_token(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token has expired or is invalid")
    return username

# Password hashing function (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Authenticate a user and return a JWT token
@app.post("/token")
async def login_for_access_token(user_data: UserLogin):
    query = select([users.c.username, users.c.password]).where(users.c.username == user_data.username)
    result = await database.fetch_one(query)
    if result is None or not pwd_context.verify(user_data.password, result['password']):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"username": user_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
# Protected route that requires a valid JWT token
@app.get("/protected")
async def protected_route(username: str = Depends(verify_token)):
    return {"message": f"Hello, {username}!"}


class UserCheck(BaseModel):
    token: str
    path: str
    method: str


# Custom authorization check method.
def check_authorization(path: str, method: str, user_role: str):
    # Check if the user is authorized for the requested path and method.
    if not enforcer.enforce(user_role, path, method):
        raise HTTPException(status_code=403, detail="Unauthorized")

@app.post("/check")
async def check(user_check: UserCheck, username: str = Depends(verify_token)):
    print("the user check ", user_check)
    # print("user check", user_check)
    # check_authorization(user_check.path, user_check.method, username)
    if username  == 'hefni':
        return {"is_authorized": True, "username": username }
    else:
        return {"is_authorized": False, "username": username }

# kegister a new user
@app.post("/register")
async def register(user_data: UserRegistration):
    hashed_password = pwd_context.hash(user_data.password)
    query = users.insert().values(username=user_data.username, password=hashed_password)
    await database.execute(query)
    return {"message": "User registered successfully"}


