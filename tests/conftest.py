from typing import TypeVar

import pytest
import redis.asyncio as redis
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer

from src.cache import CacheClient
from src.config import Settings
from src.main import get_app
from src.models import Base
from src.utils import import_models

T = TypeVar("T")


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16", driver="asyncpg") as pg:
        yield pg


@pytest.fixture(scope="session", autouse=True)
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
    try:
        yield client
    finally:
        await client.flushall()
        await client.aclose()


@pytest.fixture(scope="session")
def app(redis_container, postgres_container):
    app = get_app(
        Settings(
            postgres_url=postgres_container.get_connection_url(),
            redis_url=f"redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}",
            log_level="DEBUG"
        )
    )

    return app

@pytest.fixture(scope="session")
async def client(app: FastAPI) -> AsyncClient:
    async with app.router.lifespan_context(app), AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture(scope="session")
def cache_client(redis_client: redis.Redis, app: FastAPI):
    return CacheClient(redis_client, app.state.settings.default_cache_key_ttl)