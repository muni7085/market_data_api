from database import Base
from sqlalchemy.orm import mapped_column,Mapped
class User(Base):
    __tablename__="users"
    id:Mapped[int]= mapped_column(primary_key=True,index=True,autoincrement='auto')
    user_name:Mapped[str]
    email:Mapped[str]=mapped_column(nullable=False)
    password:Mapped[str]=mapped_column(nullable=False)
    
    def __repr__(self) -> str:
        return f"id : {self.id}\nuser_name : {self.user_name}\nemail : {self.email}\npassword : {self.password}\n"
    def __str__(self) -> str:
        return f"id : {self.id}\nuser_name : {self.user_name}\nemail : {self.email}\npassword : {self.password}\n"