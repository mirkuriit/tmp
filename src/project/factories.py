from sqlalchemy.ext.asyncio import AsyncSession

from src.project.repository import ProjectRepository


class ProjectRepositoryFactory:
    @staticmethod
    def project_repository(session: AsyncSession) -> ProjectRepository:
        return ProjectRepository(session)
