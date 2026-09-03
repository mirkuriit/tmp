from typing import Self
from uuid import UUID

from pydantic import AnyUrl, field_validator, model_validator
from pydantic_core import PydanticCustomError
from pydantic_core.core_schema import ValidationInfo

from src.schemas import Base


class ProjectBase(Base):
    name: str
    allow_experimental_functions: bool
    description: str | None = None
    logo_url: str | None = None

    @field_validator("name", "description")
    @classmethod
    def check_is_empty(cls, value: str, info: ValidationInfo):
        if isinstance(value, str) and value.strip() == "":
            raise PydanticCustomError(
                'field_is_empty',
                "{wrong_value} cannot be empty",
                dict(wrong_value=value)
            )
        return value.strip()


    @field_validator("logo_url")
    @classmethod
    def check_is_url_invalid(cls, value: str | None) -> str | None:
        if value is None:
            return value
        AnyUrl(value)
        return value




class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: UUID
    likes: int


class ProjectUpdate(ProjectBase):
    name: str | None = None
    allow_experimental_functions: bool | None = None

    @model_validator(mode="after")
    def check_is_all_none(self) -> Self:
        if not self.model_fields_set:
            raise PydanticCustomError(
                'request_is_empty',
                "No fields to update"
            )
        return self





