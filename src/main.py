import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.event.v1.router import router as event_router_v1
from src.healthchek.healthcheck_router import router as healthcheck_router
from src.middleware import LogMiddleware
from src.project.v1.router import router as project_router_v1
from src.user.v1.router import router as user_router_v1
from src.config import settings
from src.cache import  CacheClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    app.state.cache_client = CacheClient(redis_client)
    yield
    await redis_client.aclose()


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

def get_app() -> FastAPI:
    app = FastAPI(
        docs_url='/docs',
        openapi_url='/openapi.json',
        default_response_class=JSONResponse,
        lifespan=lifespan
    )

    add_routers(app)
    add_middlewares(app)

    return app

app = get_app()