from fastapi import APIRouter, Depends, Path

from app.schemas.user_model import UserSignUp,UserSignIn

router=APIRouter(prefix="/auth",tags=["authentication"])


@router.post("/signup")
async def signup(user:UserSignUp):
    """
    Sign up a new user
    """
    return user.dict()

@router.post("/signin")
async def signin(user:UserSignIn):
    """
    Sign in a user
    """
    return user.dict()