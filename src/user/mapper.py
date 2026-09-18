from sqlalchemy import Sequence

from src.llm_models.model import LLMModel
from src.project.model import Project
from src.project.schema import (
    PaginatedProjectResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from src.user.model import User, Organization, UserOrganization
from src.user.schema import UserCreate, UserResponse, PaginatedUserResponse, \
    UserUpdate


class UserMapper:
    @staticmethod
    def schema_to_model(data: UserCreate) -> User:
        organizations = [Organization(**model.model_dump()) for model in data.organizations]
        return User(**data.model_dump(exclude={"organizations"}), organizations=organizations)

    @staticmethod
    def model_to_schema(data: User) -> UserResponse:
        from loguru import logger
        logger.info(f"Data: {data.organizations} ,{type(data.organizations)}")
        logger.info(f"Data: {data.organizations} ,{type(data.organizations)}")
        return UserResponse.model_validate(data)

    @staticmethod
    def models_to_pagination_schema(users: Sequence[User]) -> PaginatedUserResponse:
        if not users:
            return PaginatedUserResponse(
                items=users,
                last_seen_id=None,
                last_seen_datetime=None
            )
        return PaginatedUserResponse(
            items=users,
            last_seen_id=users[-1].id,
            last_seen_datetime=users[-1].created_at
        )


    @staticmethod
    def update_model_from_schema(data: User, updated_data: UserUpdate) -> User:
        for field, value in updated_data.model_dump(exclude_unset=True, exclude={"organizations"}).items():
            setattr(data, field, value)

        if "organizations" in updated_data.model_fields_set and updated_data.organizations:
            models_by_id = {model.id: model for model in data.organizations}
            for updated_model in updated_data.organizations:
                model = models_by_id.get(updated_model.id)
                if model is None:
                    continue
                for field, value in updated_model.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(model, field, value)

        return data