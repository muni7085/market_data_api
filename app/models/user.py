from sqlmodel import SQLModel, Field



class User(SQLModel, table=True):
    username: str = Field(default=None, primary_key=True)
    email: str 
    full_name: str or None = None
    disabled: bool or None = None
    password:str
    
class CreateUser(SQLModel):
    username: str = Field(default=None, primary_key=True)
    email: str 
    full_name: str or None = None
    password:str
    
class LoginUser(SQLModel):
    username: str
    password:str