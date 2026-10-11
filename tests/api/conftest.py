import pytest
import sqlalchemy as sa
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings, Settings
from src.utils import import_models
from src.main import get_app


@pytest.fixture(scope="session")
def app(redis_container, postgres_container):
    app = get_app(
        Settings(
            postgres_url=postgres_container.get_connection_url(),
            redis_url=f"redis://{redis_container.get_container_host_ip()}:{redis_container.port}",
            log_level="DEBUG"
        )
    )

    return app

@pytest.fixture(scope="session")
async def client(app: FastAPI) -> AsyncClient:
    async with app.router.lifespan_context(app):
        async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client
