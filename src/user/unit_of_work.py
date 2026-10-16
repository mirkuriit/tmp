from typing import Self

from src.user.factories import UserRepositoryFactory, UserServiceFactory


class UserUOW:
    def __init__(self, session_factory, service_factory: UserServiceFactory, repository_factory: UserRepositoryFactory):
        self._session_factory = session_factory
        self._service_factory = service_factory
        self._repository_factory = repository_factory

    async def __aenter__(self) -> Self:
        self.session = self._session_factory()
        self._transaction = await self.session.begin()
        self.organization_service = self._service_factory.organization_service(self.session)
        self.user_organization_service = self._service_factory.user_organization_service(self.session)
        self.repository = self._repository_factory.user_repository(self.session)

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
