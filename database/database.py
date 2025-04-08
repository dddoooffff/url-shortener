from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

engine = create_async_engine(url=settings.DATABASE_URL)

asyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    