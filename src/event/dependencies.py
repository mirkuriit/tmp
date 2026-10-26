from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from src.cache import CacheClient, cache_client_dependency
from src.db import SessionDependency, UnitOfWork, uow_dependency
from src.event.mapper import EventMapper
from src.event.repository import EventRepository
from src.event.service import EventService
from src.event.service_moderation_decision_client import ModerationDecisionClient


def event_repository_dependency(db_session: SessionDependency) -> EventRepository:
    return EventRepository(db_session)


def event_mapper() -> EventMapper:
    return EventMapper()


def moderation_api_url_dependency(request: Request) -> str:
    return request.app.state.moderation_api_url


def http_moderation_decision_client_dependency(request: Request) -> ModerationDecisionClient:
    return request.app.state.moderation_decision_client


def event_service_dependency(
        cache_client: Annotated[CacheClient, Depends(cache_client_dependency)],
        moderation_decision_client: Annotated[ModerationDecisionClient, Depends(http_moderation_decision_client_dependency)],
        mapper: Annotated[EventMapper, Depends(event_mapper)],
        uow: Annotated[UnitOfWork, Depends(uow_dependency)],
        repository: Annotated[EventRepository, Depends(event_repository_dependency)],
) -> EventService:
    return EventService(
        cache_client=cache_client,
        moderation_decision_client=moderation_decision_client,
        repository=repository,
        mapper=mapper,
        uow=uow,

    )