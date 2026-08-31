from src.project.model import Project
from src.project.schema import ProjectCreate, ProjectResponse, ProjectUpdate


class ProjectMapper:
    @staticmethod
    def schema_to_model(data: ProjectCreate) -> Project:
        return Project(**data.model_dump())

    @staticmethod
    def model_to_schema(data: Project) -> ProjectResponse:
        return ProjectResponse.model_validate(data)

    @staticmethod
    def update_model_from_schema(data: Project, updated_data: ProjectUpdate) -> Project:
        for field, value in updated_data.model_dump(exclude_unset=True).items():
            setattr(data, field, value)
        return data