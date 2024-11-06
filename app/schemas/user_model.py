from pydantic import BaseModel

class UserSignIn(BaseModel):
    """
    UserSignIn model represents the user sign in information
    """
    email: str
    password: str

class UserSignUp(UserSignIn):
    """
    UserSignUp model represents the user sign up information
    """
    full_name: str
    phone_number: str
    confirm_password: str
    gender: str

