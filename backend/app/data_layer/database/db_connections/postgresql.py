from pathlib import Path
from typing import Generator
from urllib.parse import quote_plus

from sqlmodel import Session, SQLModel, create_engine

from app.utils.common.logger import get_logger
from app.utils.fetch_data import get_required_env_var

logger = get_logger(Path(__file__).name)


# Get the database connection details from the environment variables
user_name = get_required_env_var("POSTGRES_USER")
password = get_required_env_var("POSTGRES_PASSWORD")
host = get_required_env_var("POSTGRES_HOST")
port = get_required_env_var("POSTGRES_PORT")
db_name = get_required_env_var("POSTGRES_DB")

DATABASE_URL = f"postgresql://{quote_plus(user_name)}:{quote_plus(password)}@{host}:{port}/{db_name}"


engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    """
    Create the database and tables if they do not exist
    """
    logger.info("Creating database and tables")
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database and tables created successfully")
    except Exception as e:
        logger.error("Failed to create database and tables: %s", e)
        raise


def get_session() -> Generator[Session, None, None]:
    """
    Create a new session and return it
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error("Database session error: %s", e)
            raise
