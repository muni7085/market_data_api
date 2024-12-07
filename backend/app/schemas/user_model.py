from pydantic import BaseModel


class UserSignup(BaseModel):
    """
    UserSignup schema for user registration
    """

    user_id: str
    username: str
    email: str
    password: str
    confirm_password: str
    date_of_birth: str
    phone_number: str
    gender: str


class UserSignIn(BaseModel):
    """
    UserSignIn schema for user authentication
    """

    email: str
    password: str
