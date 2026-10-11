import pytest
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, \
    create_async_engine, async_sessionmaker
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer

from src.cache import CacheClient
from src.models import Base
from src.utils import import_models
from typing import TypeVar

T = TypeVar("T")


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16", driver="asyncpg") as pg:
        yield pg


@pytest.fixture(scope="session")
async def db_engine(postgres_container: PostgresContainer):
    engine = create_async_engine(postgres_container.get_connection_url())
    import_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
async def db_session(db_engine: AsyncEngine):
    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7") as redis:
        yield redis



@pytest.fixture(scope="session")
async def redis_client(redis_container: RedisContainer):
    host = redis_container.get_container_host_ip()
    port = redis_container.get_exposed_port(6379)
    client = redis.Redis.from_url(f"redis://{host}:{port}/0", decode_responses=True)
    yield client
    await client.flushall()
    await client.aclose()


@pytest.fixture(scope="session")
def cache_client(redis_client: redis.Redis):
    return CacheClient(redis_client)