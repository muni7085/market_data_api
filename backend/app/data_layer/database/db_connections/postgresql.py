from sqlmodel import create_engine, SQLModel, Session, select
import os
from dotenv import load_dotenv
from app import ROOT_DIR

load_dotenv(ROOT_DIR.parent / ".env")

user_name = os.environ.get("POSTGRES_USER")
password = os.environ.get("POSTGRES_PASSWORD")
host = os.environ.get("POSTGRES_HOST")
port = os.environ.get("POSTGRES_PORT")
db_name = os.environ.get("POSTGRES_DB")

DATABASE_URL = f"postgresql://{user_name}:{password}@{host}:{port}/{db_name}"

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    print("Creating database and tables")
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
