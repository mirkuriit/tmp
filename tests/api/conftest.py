import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.config import Settings
from src.main import get_app


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
