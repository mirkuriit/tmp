import asyncio
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings
from src.db import UnitOfWork
from src.event.exceptions import EventNotFoundError, \
    ModerationDecisionClientExternalError
from src.event.model import ModerationDecisionStatus
from src.event.schema import ModerationDecisionResponse
from src.event.service import EventService
from src.event.service_moderation_decision_client import \
    ModerationDecisionClient, RetryBudget
from src.worker import celery
from src.event.repository import EventRepository


class EventWorkerFactory:
    def __init__(self, session: AsyncSession, http_client: httpx.AsyncClient):
        self._session = session
        self._http_client = http_client

    def event_repository(self) -> EventRepository:
        return EventRepository(self._session)

    def moderation_decision_client(self) -> ModerationDecisionClient:
        return ModerationDecisionClient(
            client=self._http_client,
            max_retry_count=settings.max_retry_count,
            max_delay_ms=settings.max_delay_ms,
            delay_base_ms=settings.delay_base_ms,
            retry_budget=RetryBudget(settings.allowed_retries_percentage),
            moderation_api_url=settings.moderation_api_url,
        )


async def process_pending_event(moderation_decision: dict[str, Any], event_id: UUID):
    engine = create_async_engine(settings.postgres_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session, httpx.AsyncClient() as http_client:
        worker_factory = EventWorkerFactory(session=session, http_client=http_client)

        repository = worker_factory.event_repository()
        moderation_decision_client = worker_factory.moderation_decision_client()


        event = await repository.get_one_or_none(event_id=event_id)

        if not event:
            raise EventNotFoundError("event nopt found")

        try:
            moderation_decision = await moderation_decision_client.post_response(
                json=moderation_decision,
                response_model=ModerationDecisionResponse,
                idempotency_key=event_id
            )
        except Exception as ex:
            await repository.set_moderation_decision_status(
                event=event,
                status=ModerationDecisionStatus.FAILED,
                moderation_decision_id=None
            )
            await session.commit()
            raise ex

        await repository.set_moderation_decision_status(
            event=event,
            status=ModerationDecisionStatus.COMPLETED,
            moderation_decision_id=moderation_decision.id,
        )
        await session.commit()

@celery.task(
    autoretry_for=(ModerationDecisionClientExternalError,),
    retry_backoff=5,
    max_retries=5,


)
def try_recover_moderation_decision(moderation_decision: dict[str, Any], event_id: str) -> None:
    asyncio.run(process_pending_event(moderation_decision, UUID(event_id)))