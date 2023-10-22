from sqlmodel import SQLModel, create_engine
from urllib.parse import quote
import os


db_password = quote(os.environ.get("MARKET_DB_PASSWORD"))
db_url = f"postgresql://munikumar:{db_password}@localhost:5432/market_data"


engine = create_engine(db_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
