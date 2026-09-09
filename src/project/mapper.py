from loguru import logger

from src import llm_models
from src.llm_models.model import LLMModel
from src.project.model import Project
from src.project.schema import ProjectCreate, ProjectResponse, ProjectUpdate


class ProjectMapper:
    @staticmethod
    def schema_to_model(data: ProjectCreate) -> Project:
        llm_models = [LLMModel(**model.model_dump()) for model in data.llm_models]
        Project()
        return Project(**data.model_dump(exclude="llm_models"), llm_models=llm_models)

    @staticmethod
    def model_to_schema(data: Project) -> ProjectResponse:
        return ProjectResponse.model_validate(data)

    @staticmethod
    def update_model_from_schema(data: Project, updated_data: ProjectUpdate) -> Project:
        for field, value in updated_data.model_dump(exclude_unset=True).items():
            if field == "llm_models":
                data.llm_models = [LLMModel(**model) for model in value]
            else:
                setattr(data, field, value)
        return data