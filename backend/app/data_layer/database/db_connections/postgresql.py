import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

from app import ROOT_DIR

load_dotenv(ROOT_DIR.parent / ".env")

# Get the database connection details from the environment variables
user_name = os.environ.get("POSTGRES_USER")
password = os.environ.get("POSTGRES_PASSWORD")
host = os.environ.get("POSTGRES_HOST")
port = os.environ.get("POSTGRES_PORT")
db_name = os.environ.get("POSTGRES_DB")

DATABASE_URL = f"postgresql://{user_name}:{password}@{host}:{port}/{db_name}"

engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    """
    Create the database and tables if they do not exist
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Create a new session and return it
    """
    with Session(engine) as session:
        yield session
