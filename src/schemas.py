import datetime as dt
from typing import Self
from uuid import UUID

from pydantic import BaseModel, model_validator
from pydantic_core import PydanticCustomError


class Base(BaseModel):
    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    last_seen_datetime: dt.datetime | None
    last_seen_id: UUID | None


class BaseUpdateValidationMixin(BaseModel):
    @model_validator(mode="after")
    def check_is_all_none(self) -> Self:
        if not self.model_fields_set:
            raise PydanticCustomError('request_is_empty', "No fields to update")
        return self