import datetime as dt
from typing import Self
from uuid import UUID

from pydantic import field_validator, model_validator
from pydantic_core import PydanticCustomError

from src.event.exceptions import InvalidStartDateError
from src.event_info.schema import EventInfoCreate, EventInfoResponse, EventInfoUpdate
from src.schemas import Base, BaseUpdateValidationMixin, PaginatedResponse


class EventBase(Base):
     name: str
     description: str
     start_date: dt.datetime
     end_date: dt.datetime

     @field_validator("name", "description")
     @classmethod
     def check_is_empty(cls, value: str):
         if isinstance(value, str) and value.strip() == "":
             raise PydanticCustomError(
                 'field_is_empty',
                 "{wrong_value} cannot be empty",
                 {"wrong_value": value}
             )
         return value.strip() if value else value

     @model_validator(mode='after')
     def check_is_valid_date(self) -> Self:
         if self.end_date and self.start_date and self.end_date < self.start_date:
            raise InvalidStartDateError(
                start_date=self.start_date,
                end_date=self.end_date
            )
         return self


class ModerationDecisionBase(Base):
    comment: str
    is_allowed: bool


class ModerationDecisionCreate(ModerationDecisionBase):
    pass


class ModerationDecisionResponse(ModerationDecisionBase):
    id: UUID
    idempotency_key: UUID


class EventResponse(EventBase):
    id: UUID
    moderation_decision_id: UUID | None = None
    event_info: EventInfoResponse
    moderation_decision: ModerationDecisionResponse | None = None

class EventManyResponse(EventBase):
    id: UUID
    moderation_decision_id: UUID | None = None
    event_info: EventInfoResponse

class PaginatedEventResponse(Base, PaginatedResponse):
    items: list[EventManyResponse]


class EventCreate(EventBase):
    event_info: EventInfoCreate
    moderation_decision: ModerationDecisionCreate


class EventUpdate(EventBase, BaseUpdateValidationMixin):
    name: str | None = None
    description: str | None = None
    start_date: dt.datetime | None = None
    end_date: dt.datetime | None = None
    event_info: EventInfoUpdate | None = None
