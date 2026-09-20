import datetime as dt
from typing import Self
from uuid import UUID

from pydantic import field_validator, model_validator, Field
from pydantic_core import PydanticCustomError

from src.schemas import Base, PaginatedResponse, BaseUpdateValidationMixin


class EventInfoBase(Base):
    organizer: str | None = None
    head_url: str | None = Field(default=None, examples=["https://example.com/"])
    location: str | None = None


class EventInfoCreate(EventInfoBase):
    pass


class EventInfoUpdate(EventInfoBase):
    pass


class EventInfoResponse(EventInfoBase):
    id: UUID


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
                raise PydanticCustomError(
                    "start_date_greater_than_end",
                    "start_date:{start_date} can not be greater than end_date:{end_date}",
                    {"start_date": self.start_date, "end_date": self.end_date}
                )
         return self


class EventResponse(EventBase):
    id: UUID
    event_info: EventInfoResponse


class PaginatedEventResponse(Base, PaginatedResponse):
    items: list[EventResponse]


class EventCreate(EventBase):
    event_info: EventInfoCreate


class EventUpdate(EventBase, BaseUpdateValidationMixin):
    name: str | None = None
    description: str | None = None
    start_date: dt.datetime | None = None
    end_date: dt.datetime | None = None
    event_info: EventInfoUpdate | None = None
