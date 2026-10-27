
from fastapi import HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from src.event.exceptions import (
    ModerationDecisionClientExternalError,
    ModerationDecisionClientInternalError,
)
from src.event.mapper import EventMapper
from src.event.model import ModerationDecisionStatus
from src.event.schema import EventCreate, EventResponse, ModerationDecisionResponse
from src.event.service import EventService
from src.event.service_moderation_decision_client import ModerationDecisionClient


class CreateEventSaga:
    def __init__(
            self,
            event_service: EventService,
            moderation_decision_client: ModerationDecisionClient,
            mapper: EventMapper
    ) -> None:
        self._event_service = event_service
        self._moderation_decision_client = moderation_decision_client
        self._mapper = mapper

    async def run(self, data: EventCreate) -> EventResponse:
        try:
            event = await self._event_service.create(data)


            moderation_decision = await self._moderation_decision_client.post_response(
                json=self._mapper.schema_to_dict(data.moderation_decision),
                response_model=ModerationDecisionResponse,
                idempotency_key=event.id
            )

            event = await self._event_service.set_moderation_decision_status(
                event_id=event.id,
                status=ModerationDecisionStatus.COMPLETED,
                moderation_decision_id=moderation_decision.id
            )

            event.moderation_decision = moderation_decision
            return event

        except ModerationDecisionClientInternalError as ex:
            # ничего т.к. мы накосячили с контрактом,
            await self._event_service.delete(event_id=event.id)
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.message
            )

        except ModerationDecisionClientExternalError:
            # TODO: запустить фоном воркер
            event = await self._event_service.set_moderation_decision_status(
                event_id=event.id,
                status=ModerationDecisionStatus.PENDING,
                moderation_decision_id=None
            )
            return event