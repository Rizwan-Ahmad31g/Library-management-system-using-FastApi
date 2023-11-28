from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from app.models.user_authentication_model import Token
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter
from app.api.database.config import user_authetication_collection
from app.models.user_authentication_model import UserInDB, TokenData
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import json
from passlib.context import CryptContext

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
router_cred = APIRouter(
    tags=["Enter user credentials"]
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router_cred.put("/authetication")
def enter_user_credentials(user: Annotated[str, Query(description="Enter name")],
                           password: Annotated[str, Query(description="Create Password")],
                           reenter: Annotated[str, Query(description="Reenter your password")] = None):
    user_password = get_password_hash(password)
    user_reenter = get_password_hash(reenter)
    user_id = user_authetication_collection.find_one({"username": user}, {"username": 1, "_id": 0})
    if user_id is not None:
       raise HTTPException(status_code=400 , detail="User name already taken")
    else:
        if password == reenter:
            user_credentials = {
                "username": user,
                "hashed_password": user_password
            }
            data_entry = user_authetication_collection.insert_one(user_credentials)

            if data_entry:
                raise HTTPException(status_code=200, detail="user created succesfully")
        else:
            raise HTTPException(status_code=400, detail="password doest not match")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(database, username: str):
    user_data = user_authetication_collection.find_one({"username": username}, {"_id": 0})
    if user_data:
        return UserInDB(username=user_data["username"], hashed_password=user_data["hashed_password"])


def authenticate_user(user_db_collection, username: str, password: str):
    user = get_user(user_db_collection, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
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


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user_db_collection = user_authetication_collection.find_one({"username": username}, {"_id": 0})
    user = get_user(user_db_collection, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router_cred.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user_db_collection = user_authetication_collection.find_one({"username": form_data.username}, {"_id": 0})
    user_data = json.dumps(user_db_collection)
    user_collection_data = json.loads(user_data)
    user = authenticate_user(user_collection_data, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
