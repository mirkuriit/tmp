from sqlalchemy import Sequence

from src.event.model import Event, EventInfo
from src.event.schema import EventCreate, EventResponse, \
    PaginatedEventResponse, EventUpdate

class EventMapper:
    @staticmethod
    def schema_to_model(data: EventCreate) -> Event:
        return Event(
            **data.model_dump(exclude={"event_info"}),
            event_info=EventInfo(**data.event_info.model_dump())
        )

    @staticmethod
    def model_to_schema(data: Event) -> EventResponse:
        return EventResponse.model_validate(data)

    @staticmethod
    def models_to_pagination_schema(events: Sequence[Event]) -> PaginatedEventResponse:
        if not events:
            return PaginatedEventResponse(
                items=events,
                last_seen_id=None,
                last_seen_datetime=None
            )
        return PaginatedEventResponse(
            items=events,
            last_seen_id=events[-1].id,
            last_seen_datetime=events[-1].created_at
        )


    @staticmethod
    def update_model_from_schema(data: Event, updated_data: EventUpdate) -> Event:
        for field, value in updated_data.model_dump(exclude_unset=True, exclude={"event_info"}).items():
            setattr(data, field, value)

        from loguru import logger
        logger.info(f"data {data}")


        if "event_info" in updated_data.model_fields_set and updated_data.event_info:
            logger.info(f"updated data {updated_data}")
            for field, value in updated_data.event_info.model_dump(exclude_unset=True, exclude={"id"}).items():
                setattr(data.event_info, field, value)

        return data