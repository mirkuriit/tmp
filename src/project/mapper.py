from src.project.model import Project
from src.project.schema import ProjectCreate, ProjectResponse

class ProjectMapper:
    @staticmethod
    def schema_to_model(data: ProjectCreate) -> Project:
        return Project(**data.model_dump())

    @staticmethod
    def model_to_schema(data: Project) -> ProjectResponse:
        return ProjectResponse.model_validate(data)