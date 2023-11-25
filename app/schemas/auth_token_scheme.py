from pydantic import BaseModel
from app.utils.constants import SECRET_KEY


class TokenData(BaseModel):
    username: str or None = None
    password: str or None = None


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class RefreshToken(AccessToken):
    refresh_token: str


class Settings(BaseModel):
    authjwt_secret_key: str = SECRET_KEY
