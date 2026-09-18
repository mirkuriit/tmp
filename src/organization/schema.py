import datetime as dt
from uuid import UUID

from pydantic import AnyUrl, Field, field_validator
from pydantic_core import PydanticCustomError

from src.llm_models.schema import LLMModelCreate, LLMModelResponse, LLMModelUpdate
from src.schemas import Base, BaseUpdateValidationMixin


class OrganizationBase(Base):
    name: str
    description: str | None = None
    logo_url: str = Field(default="https://example.com/")


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


    @field_validator("logo_url")
    @classmethod
    def check_is_url_invalid(cls, value: str | None) -> str | None:
        if value is None:
            return value
        AnyUrl(value)
        return value


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    id: UUID