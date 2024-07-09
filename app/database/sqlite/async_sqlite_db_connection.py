from sqlalchemy.ext.asyncio import create_async_engine
from app.utils.urls import ASYNC_SQLITE_DB_URL
from sqlmodel.ext.asyncio.session import AsyncSession


aysnc_sqlite_engine = create_async_engine(ASYNC_SQLITE_DB_URL)


async def get_async_sqlite_session():
    async with AsyncSession(aysnc_sqlite_engine) as session:
        yield session
