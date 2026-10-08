from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache import cache_client
from src.db import get_read_session, get_session
from src.organization.mapper import OrganizationMapper
from src.organization.repository import OrganizationRepository
from src.organization.service import OrganizationService
from src.user.mapper import UserMapper
from src.user.repository import UserRepository
from src.user.service import UserService
from src.user_organizations.mapper import UserOrganizationMapper
from src.user_organizations.repository import UserOrganizationRepository
from src.user_organizations.service import UserOrganizationService


def user_service_dependency(session_dependency: Callable[..., Any]) -> Callable[[AsyncSession], UserService]:
    def dependency(
        session: Annotated[AsyncSession, Depends(session_dependency)],
    ) -> UserService:
        user_repository = UserRepository(session)
        user_mapper = UserMapper()

        organization_repository = OrganizationRepository(session)
        organization_mapper = OrganizationMapper()
        organization_service = OrganizationService(
            organization_repository,
            organization_mapper
        )

        user_organization_repository = UserOrganizationRepository(session)
        user_organization_mapper = UserOrganizationMapper()
        user_organization_service = UserOrganizationService(
            user_organization_repository,
            user_organization_mapper
        )

        user_cache_client = cache_client

        return UserService(
            user_repository,
            user_mapper,
            organization_service,
            user_organization_service,
            user_cache_client
        )

    return dependency


get_read_user_service = user_service_dependency(get_read_session)
get_user_service = user_service_dependency(get_session)