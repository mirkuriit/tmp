from sqlalchemy.ext.asyncio import AsyncSession

from src.organization.mapper import OrganizationMapper
from src.organization.repository import OrganizationRepository
from src.organization.service import OrganizationService
from src.user_organizations.mapper import UserOrganizationMapper
from src.user_organizations.repository import UserOrganizationRepository
from src.user_organizations.service import UserOrganizationService


class UserServiceFactory:
    @staticmethod
    def organization_service(session: AsyncSession) -> OrganizationService:
        return OrganizationService(
            repository=OrganizationRepository(session),
            mapper=OrganizationMapper(),
        )

    @staticmethod
    def user_organization_service(session: AsyncSession) -> UserOrganizationService:
        return UserOrganizationService(
            repository=UserOrganizationRepository(session),
            mapper=UserOrganizationMapper(),
        )
