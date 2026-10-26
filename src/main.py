from contextlib import asynccontextmanager

import httpx
import redis.asyncio as redis
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.cache import CacheClient
from src.config import Settings, settings
from src.event.service_moderation_decision_client import (
    ModerationDecisionClient,
    RetryBudget,
)
from src.event.v1.router import router as event_router_v1
from src.healthchek.healthcheck_router import router as healthcheck_router
from src.middleware import LogMiddleware
from src.project.v1.router import router as project_router_v1
from src.user.v1.router import router as user_router_v1


def make_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        redis_client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True
        )
        app.state.cache_client = CacheClient(
            client=redis_client,
            default_cache_key_ttl=settings.default_cache_key_ttl,
        )

        engine = create_async_engine(settings.postgres_url, pool_pre_ping=True)
        app.state.db_engine = engine
        app.state.SessionFactory = async_sessionmaker(engine, expire_on_commit=False)

        app.state.moderation_api_url = settings.moderation_api_url
        httpx_client = httpx.AsyncClient()
        retry_budget = RetryBudget(settings.allowed_retries_percentage)
        app.state.moderation_decision_client = ModerationDecisionClient(
            client=httpx_client,
            max_retry_count=settings.max_retry_count,
            max_delay_ms=settings.max_delay_ms,
            delay_base_ms=settings.delay_base_ms,
            retry_budget=retry_budget,
            moderation_api_url=settings.moderation_api_url
        )

        try:
            yield
        finally:
            await redis_client.aclose()
            await httpx_client.aclose()
            await engine.dispose()

    return lifespan

def add_routers(app: FastAPI) -> None:
    app.include_router(healthcheck_router)
    app.include_router(project_router_v1)
    app.include_router(user_router_v1)
    app.include_router(event_router_v1)


def add_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.add_middleware(LogMiddleware)

def get_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        docs_url='/docs',
        openapi_url='/openapi.json',
        default_response_class=JSONResponse,
        lifespan=make_lifespan(settings),
    )
    app.state.settings = settings

    add_routers(app)
    add_middlewares(app)

    return app

app = get_app(settings)