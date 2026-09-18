from sqlalchemy import Sequence

from src.llm_models.model import LLMModel
from src.project.model import Project
from src.project.schema import (
    PaginatedProjectResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)


class ProjectMapper:
    @staticmethod
    def schema_to_model(data: ProjectCreate) -> Project:
        llm_models = [LLMModel(**model.model_dump()) for model in data.llm_models]
        return Project(**data.model_dump(exclude={"llm_models"}), llm_models=llm_models)

    @staticmethod
    def model_to_schema(data: Project) -> ProjectResponse:
        return ProjectResponse.model_validate(data)

    @staticmethod
    def models_to_pagination_schema(projects: Sequence[Project]) -> PaginatedProjectResponse:
        if not projects:
            return PaginatedProjectResponse(
                items=projects,
                last_seen_id=None,
                last_seen_datetime=None
            )
        return PaginatedProjectResponse(
            items=projects,
            last_seen_id=projects[-1].id,
            last_seen_datetime=projects[-1].created_at
        )



    @staticmethod
    def update_model_from_schema(data: Project, updated_data: ProjectUpdate) -> Project:
        for field, value in updated_data.model_dump(exclude_unset=True, exclude={"llm_models"}).items():
            setattr(data, field, value)

        if "llm_models" in updated_data.model_fields_set and updated_data.llm_models:
            models_by_id = {model.id: model for model in data.llm_models}
            for updated_model in updated_data.llm_models:
                model = models_by_id.get(updated_model.id)
                if model is None:
                    continue
                for field, value in updated_model.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(model, field, value)

        return data