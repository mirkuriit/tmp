from decimal import Decimal
from uuid import UUID

from pydantic import AnyUrl, Field, field_validator
from pydantic_core import PydanticCustomError

from src.schemas import Base, BaseUpdateValidationMixin


class LLMModelBase(Base):
    name: str
    description: str | None = None
    base_api_url: str | None = Field(default="https://example.com/")
    token_cost: Decimal

    @field_validator("token_cost")
    @classmethod
    def check_is_token_invalid(cls, value: Decimal) -> Decimal | None:
        if value >= 0:
            return value

        raise PydanticCustomError(
            "decimal_is_negative",
            "cost {wrong_value} cannot be negative",
            {"wrong_value": value}
        )


    @field_validator("name", "description")
    @classmethod
    def check_is_empty(cls, value: str):
        if isinstance(value, str) and value.strip() == "":
            raise PydanticCustomError(
                'field_is_empty',
                "{wrong_value} cannot be empty",
                {"wrong_value": value}
            )
        return value.strip()


    @field_validator("base_api_url")
    @classmethod
    def check_is_url_invalid(cls, value: str | None) -> str | None:
        if value is None:
            return value
        AnyUrl(value)
        return value


class LLMModelCreate(LLMModelBase):
    pass


class LLMModelUpdate(LLMModelBase, BaseUpdateValidationMixin):
    id: UUID
    name: str | None = None
    token_cost: Decimal | None = None


class LLMModelResponse(LLMModelBase):
    id: UUID
    project_id: UUID

