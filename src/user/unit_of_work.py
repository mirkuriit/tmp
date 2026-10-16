from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.organization.mapper import OrganizationMapper
from src.organization.repository import OrganizationRepository
from src.organization.service import OrganizationService
from src.user.repository import UserRepository, UserRepositoryFactory
from src.user.service_factory import UserServiceFactory
from src.user_organizations.repository import UserOrganizationRepository
from src.user_organizations.service import UserOrganizationService

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
