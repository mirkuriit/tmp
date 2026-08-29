from collections.abc import Callable

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import Settings

settings = Settings()

engine: AsyncEngine = create_async_engine(
    str(settings.postgres_url),
    pool_pre_ping=True,
)

SessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

def get_session(read_only: bool = False) -> Callable:
    async def wrapper() -> AsyncSession:
        async with SessionFactory() as session:
            try:
                yield session
                if not read_only:
                    await session.commit()

            except Exception:
                await session.rollback()
                raise
    return wrapper
