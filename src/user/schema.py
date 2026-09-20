import datetime as dt
from uuid import UUID

from pydantic import AnyUrl, Field, field_validator
from pydantic_core import PydanticCustomError

from src.llm_models.schema import LLMModelCreate, LLMModelResponse, LLMModelUpdate
from src.organization.schema import OrganizationCreate, OrganizationResponse, \
    OrganizationUpdate
from src.schemas import Base, BaseUpdateValidationMixin, PaginatedResponse


class UserBase(Base):
    username: str
    bio: str | None = None
    logo_url: str | None = Field(default="https://example.com/")
    has_premium: bool

    @field_validator("username", "bio")
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


class UserCreate(UserBase):
    organizations: list[OrganizationCreate]


class UserResponse(UserBase):
    id: UUID
    organizations: list[OrganizationResponse]


class PaginatedUserResponse(Base, PaginatedResponse):
    items: list[UserResponse]


class UserUpdate(UserBase, BaseUpdateValidationMixin):
    username: str | None
    has_premium: bool | None
    organizations: list[OrganizationUpdate] | None = None
