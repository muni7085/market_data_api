# from fastapi import APIRouter, Depends, HTTPException, status, Request

# from app.models.user import User, CreateUser
# from app.schemas.auth_token_scheme import AccessToken, TokenData, RefreshToken
# from app.utils.constants import (
#     ACCESS_TOKEN_EXPIRE_MINUTES,
#     ALGORITHM,
#     REFRESH_TOKEN_EXPIRE_MINUTES,
# )
# from app.routers.authentication.user_authentication import authenticate_user, get_user
# from app.routers.authentication.create_user import verify_and_register_user
# from fastapi_jwt_auth import AuthJWT

# from app.schemas.auth_token_scheme import Settings


# router = APIRouter()


# @AuthJWT.load_config
# def get_config():
#     return Settings()


# @router.post("/user/login", response_model=RefreshToken)
# async def login_for_access_token(token_data: TokenData, Authorize: AuthJWT = Depends()):
#     user = authenticate_user(token_data.username, token_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = Authorize.create_access_token(
#         subject=user.username,
#         expires_time=ACCESS_TOKEN_EXPIRE_MINUTES,
#         algorithm=ALGORITHM,
#     )
#     refresh_token = Authorize.create_refresh_token(
#         subject=user.username,
#         expires_time=REFRESH_TOKEN_EXPIRE_MINUTES,
#         algorithm=ALGORITHM,
#     )
#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#     }


# @router.post("/user/refresh", response_model=AccessToken)
# async def refresh_token(Authorize: AuthJWT = Depends()):
#     Authorize.jwt_refresh_token_required()
#     current_user = Authorize.get_jwt_subject()
#     access_token = Authorize.create_access_token(
#         subject=current_user,
#         expires_time=ACCESS_TOKEN_EXPIRE_MINUTES,
#         algorithm=ALGORITHM,
#     )
#     return {"access_token": access_token}


# @router.post("/user/register", response_model=User, status_code=status.HTTP_201_CREATED)
# async def register_user(create_user: CreateUser):
#     return verify_and_register_user(create_user)


# @router.get("/user/me", response_model=User)
# def user_me(Authorize: AuthJWT = Depends()):
#     Authorize.jwt_required()
#     current_user = Authorize.get_jwt_subject()
#     return {"username": get_user(current_user)}
