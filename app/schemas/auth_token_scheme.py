from pydantic import BaseModel


class TokenData(BaseModel):
    username: str or None = None
    password: str or None = None


class Token(BaseModel):
    access_token: str
    token_type: str
