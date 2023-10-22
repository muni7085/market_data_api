from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import User
from app.schemas.auth_token_scheme import Token
from app.utils.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from app.routers.authentication.jwt_token import create_access_token
from datetime import timedelta
from app.routers.authentication.user_authentication import authenticate_user
from app.database.db_connection import engine
from sqlmodel import Session

from temporary.oauth.main import get_password_hash

router = APIRouter()


@router.post("/user/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/user/register",response_model=User,status_code=status.HTTP_201_CREATED)
async def register_user(user:User):
    with Session(engine) as session:
        user.password=get_password_hash(user.password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user