import jwt
from datetime import timedelta, datetime
from passlib.context import CryptContext
from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.security.oauth2 import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from auth.schemas import UserCreate
from config.config import settings
from database.dao import DatabaseWork
from database.db import get_session

app = FastAPI() #выполнить в виде роутера с возможным путем auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_TIME = 30

def get_database(session: AsyncSession = Depends(get_session)):
    return DatabaseWork(session)

def check_password(password: str):
    if len(password) < 5 or len(password) > 20:
        if password.upper() == password or password.lower() == password:
            if password.isdigit() or password.isalpha():
                raise HTTPException(status_code=404, detail="wrong password need: 1 uppercase, 1 lowercase, 1 number")
    return password

def verify_password(password: str, hash_password: str):
    return pwd_context.verify(password, hash_password)

def get_hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_jwt_token(data: dict, access_expire: int | None = None):
    if access_expire:
        expire = datetime.now() + timedelta(minutes=access_expire)
    else:
        expire = datetime.now() + timedelta(minutes=15)
    data["exp"] = expire
    return jwt.encode(payload=data, key=SECRET_KEY, algorithm=ALGORITHM)

async def get_user_from_jwt_token(token: str = Depends(oauth2_scheme),
                            db: DatabaseWork = Depends(get_database)):
    exc = HTTPException(status_code=401,
                        detail="Haven't user with this token",
                        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise exc
    except Exception:
        raise exc
    user = await db.get_user_from_db(username=username)
    if user is None:
        raise exc
    return user

@app.get("/user")
async def get_user(user: UserCreate = Depends(get_user_from_jwt_token)):
    return {"username": user.username, "password": user.password}

@app.post('/login')
async def user_login(user_data: OAuth2PasswordRequestForm = Depends(),
                     db: DatabaseWork = Depends(get_database)):
    user = await db.get_user_from_db(user_data.username)
    if not user:
        return HTTPException(status_code=401, detail="wrong username")
    if not verify_password(user_data.password, user.password):
        return HTTPException(status_code=401, detail="wrong password")
    payload = {"sub": user_data.username}
    token = create_jwt_token(payload, access_expire=ACCESS_TOKEN_EXPIRE_TIME)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/register")
async def register_user(username: str = Body(),
                        password: str = Body(),
                        db: DatabaseWork = Depends(get_database)):
    password = check_password(password)
    user = UserCreate(username=username, password=get_hash_password(password))
    result = await db.add_user_in_db(user.model_dump())
    return result