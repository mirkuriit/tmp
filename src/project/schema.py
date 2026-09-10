from uuid import UUID

from pydantic import AnyUrl, Field, field_validator
from pydantic_core import PydanticCustomError
from pydantic_core.core_schema import ValidationInfo

from src.llm_models.schema import LLMModelCreate, LLMModelResponse, LLMModelUpdate
from src.schemas import Base, BaseUpdateValidationMixin


class ProjectBase(Base):
    name: str
    allow_experimental_functions: bool
    description: str | None = None
    logo_url: str | None = Field(default="https://example.com/")

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




class ProjectCreate(ProjectBase):
    llm_models: list[LLMModelCreate]


class ProjectResponse(ProjectBase):
    id: UUID
    likes: int
    llm_models: list[LLMModelResponse]


class ProjectUpdate(ProjectBase, BaseUpdateValidationMixin):
    name: str | None = None
    allow_experimental_functions: bool | None = None
    llm_models: list[LLMModelUpdate] | None = None





