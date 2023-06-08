from sqlalchemy import create_engine
from constants import DATABASE_URL
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
session_local=sessionmaker(autoflush=False,autocommit=False,bind=engine)

class Base(DeclarativeBase):
    pass