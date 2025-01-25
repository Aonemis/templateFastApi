from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config.config import settings

DATABASE_URL = settings.get_database_url

engine = create_async_engine(url=DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

async def get_session():
    async with async_session_maker() as session:
        yield session

class Base(DeclarativeBase):
    __abstract__ = True