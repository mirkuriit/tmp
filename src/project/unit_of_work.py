from typing import Self

from src.project.factories import ProjectRepositoryFactory


class ProjectUOW:
    def __init__(self, session_factory,  repository_factory: ProjectRepositoryFactory):
        self._session_factory = session_factory
        self._repository_factory = repository_factory

    async def __aenter__(self) -> Self:
        self.session = self._session_factory()
        self._transaction = await self.session.begin()
        self.repository = self._repository_factory.project_repository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self._transaction.__aexit__(
                exc_type,
                exc_val,
                exc_tb,
            )
        finally:
            await self.session.close()