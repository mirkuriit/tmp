from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel

from src.event.model import Event
from src.event.schema import (
    EventCreate,
    EventResponse,
    EventUpdate,
    ModerationDecisionResponse,
    PaginatedEventResponse,
)
from src.event_info.model import EventInfo


class EventMapper:
    @staticmethod
    def schema_to_dict(data: BaseModel)-> dict[str, Any]:
        return data.model_dump()

    @staticmethod
    def schema_to_model(data: EventCreate) -> Event:
        return Event(
            **data.model_dump(exclude={"event_info", "moderation_decision"}),
            event_info=EventInfo(**data.event_info.model_dump())
        )

    @staticmethod
    def model_to_schema(
            data: Event,
            moderation_decision: ModerationDecisionResponse | None = None
    ) -> EventResponse:
        event_response = EventResponse.model_validate(data)
        event_response.moderation_decision = moderation_decision
        return event_response

    @staticmethod
    def models_to_pagination_schema(events: Sequence[Event]) -> PaginatedEventResponse:
        return PaginatedEventResponse(
            items=events,
            last_seen_id=events[-1].id,
            last_seen_datetime=events[-1].created_at
        )


    @staticmethod
    def update_model_from_schema(data: Event, updated_data: EventUpdate) -> Event:
        for field, value in updated_data.model_dump(exclude_unset=True, exclude={"event_info"}).items():
            setattr(data, field, value)


        if "event_info" in updated_data.model_fields_set and updated_data.event_info:
            for field, value in updated_data.event_info.model_dump(exclude_unset=True, exclude={"id"}).items():
                setattr(data.event_info, field, value)

        return data