from pydantic import BaseModel

class UserSignup(BaseModel):
    user_id: str
    username: str
    email: str
    password: str
    confirm_password: str
    date_of_birth: str
    phone_number: str
    gender: str
    
class UserSignIn(BaseModel):
    email: str
    password: str
    