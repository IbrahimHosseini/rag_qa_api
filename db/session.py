from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG, 
    pool_size=10, 
    max_overflow=20
)

AsyncSessionFactory = async_sessionmaker(
    engine,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise