import datetime as dt

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache import CacheClient
from src.db import UnitOfWork
from src.event.mapper import EventMapper
from src.event.repository import EventRepository
from src.event.schema import (
    EventCreate,
    EventResponse,
    EventUpdate,
    PaginatedEventResponse,
)
from src.event.service import EventService
from src.event_info.schema import EventInfoCreate
from src.schemas import PaginationPage
from tests.utils import compare_object_fields


@pytest.fixture(scope="session")
def repository(repository_db_session: AsyncSession) -> EventRepository:
    return EventRepository(
        repository_db_session
    )


@pytest.fixture(scope="session")
def service(
        db_session: AsyncSession,
        cache_client: CacheClient,
) -> EventService:
    return EventService(
        EventMapper(),
        cache_client,
        EventRepository(db_session),
        UnitOfWork(db_session)
    )


@pytest.fixture(scope="session")
def create_event_instance() -> EventCreate:
    return EventCreate(
        name="fish",
        description="about fish",
        start_date=dt.datetime(
            2026,
            1,
            15,
            10,
            0,
            tzinfo=dt.UTC
        ),
        end_date=dt.datetime(
            2027,
            1,
            15,
            10,
            0,
            tzinfo=dt.UTC
        ),
        event_info=EventInfoCreate(
            organizer="Ms. Fish",
            location="Peace ocean",
            head_url="example.com"
        )
    )


@pytest.fixture(scope="session")
def update_event_instance(create_event_instance: EventCreate) -> EventUpdate:
    return EventUpdate(
        name="Updated fish",
        description="Updated fish about",
        start_date=create_event_instance.start_date,
        end_date=create_event_instance.end_date
    )


@pytest.fixture(scope="session")
async def created_event_response(
        service: EventService,
        create_event_instance: EventCreate
)-> EventResponse:
    return await service.create(create_event_instance)


async def test_create_event(
        create_event_instance: EventCreate,
        created_event_response: EventResponse,
        repository: EventRepository
) -> None:
    event = await repository.get_one_or_none(created_event_response.id)
    compare_object_fields(
        event, create_event_instance, exclude={"event_info"}
    )
    compare_object_fields(
        event.event_info, create_event_instance.event_info
    )


async def test_get_event(
        create_event_instance: EventCreate,
        created_event_response: EventResponse,
        repository: EventRepository,
        service: EventService,
        cache_client: CacheClient,
) -> None:
    cache_key = cache_client.get_one_cache_key(created_event_response.id, "event")
    await cache_client.delete(cache_key)
    assert await cache_client.get_response(cache_key, EventResponse) is None

    event = await service.get_one(created_event_response.id)
    cached_event = await cache_client.get_response(cache_key, EventResponse)
    assert cached_event is not None
    assert cached_event == event
    compare_object_fields(
        event, create_event_instance, exclude={"event_info"}
    )
    compare_object_fields(
        event.event_info, create_event_instance.event_info
    )


async def test_get_many_events(
        created_event_response: EventResponse,
        service: EventService,
        cache_client: CacheClient,
        default_pagination_page: PaginationPage
) -> None:
    cache_key = await cache_client.get_many_cache_key("events", default_pagination_page)
    await cache_client.delete(cache_key)
    assert await cache_client.get_response(cache_key, PaginatedEventResponse) is None

    events = await service.get_many(default_pagination_page)
    cached_events = await cache_client.get_response(cache_key, PaginatedEventResponse)
    assert cached_events is not None
    assert cached_events == events


async def test_update_event(
        update_event_instance: EventUpdate,
        created_event_response: EventResponse,
        repository: EventRepository,
        service: EventService,
        cache_client: CacheClient,
) -> None:
    cache_key = cache_client.get_one_cache_key(created_event_response.id, "event")
    await service.get_one(created_event_response.id)
    assert await cache_client.get_response(cache_key, EventResponse) is not None

    await service.update(created_event_response.id, update_event_instance)

    event = await repository.get_one_or_none(created_event_response.id)
    compare_object_fields(
        event, update_event_instance, exclude={"event_info"}
    )


async def test_delete_event(
        update_event_instance: EventUpdate,
        created_event_response: EventResponse,
        repository: EventRepository,
        service: EventService,
) -> None:
    await service.delete(created_event_response.id)
    event = await repository.get_one_or_none(created_event_response.id)
    assert event is None





