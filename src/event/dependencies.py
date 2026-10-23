from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from src.cache import CacheClient, cache_client_dependency
from src.db import SessionDependency, UnitOfWork, uow_dependency
from src.event.mapper import EventMapper
from src.event.repository import EventRepository
from src.event.service import EventService
from src.http import HTTPClient, http_client_dependency


def event_repository_dependency(db_session: SessionDependency) -> EventRepository:
    return EventRepository(db_session)


def event_mapper() -> EventMapper:
    return EventMapper()


def moderation_api_url_dependency(request: Request) -> str:
    return request.app.state.moderation_api_url


def event_service_dependency(
        cache_client: Annotated[CacheClient, Depends(cache_client_dependency)],
        http_client: Annotated[HTTPClient, Depends(http_client_dependency)],
        mapper: Annotated[EventMapper, Depends(event_mapper)],
        uow: Annotated[UnitOfWork, Depends(uow_dependency)],
        repository: Annotated[EventRepository, Depends(event_repository_dependency)],
        moderation_api_url: Annotated[str, Depends(moderation_api_url_dependency)],
) -> EventService:
    return EventService(
        cache_client=cache_client,
        http_client=http_client,
        repository=repository,
        mapper=mapper,
        uow=uow,
        moderation_api_url=moderation_api_url

    )