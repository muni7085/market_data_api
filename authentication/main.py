from fastapi import FastAPI,Depends
from models.pydantic_m.user_model import User as PydanticUser
from models.sqlalchemy_m.user_model import Base
from models.sqlalchemy_m.user_model import User as SqlalchemyUser
from database import session_local
from database import engine
from sqlalchemy import Select
from sqlalchemy.orm import Session
from helper import to_json
import json
app=FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db=session_local()
    try:
        yield db
    finally:
        db.close()

@app.post("/authentication")
def main(request:PydanticUser,db:Session=Depends(get_db)):
    new_user=SqlalchemyUser(
        user_name=request.username,
        email=request.email,
        password=request.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
@app.get("/all-users")
def all_users(db:Session=Depends(get_db)):
    stmt=Select(SqlalchemyUser)
    users=db.scalars(stmt).all()
    user_dict=[to_json(user) for user in users]
    return user_dict