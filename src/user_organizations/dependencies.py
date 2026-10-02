from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_read_session, get_session
from src.user_organizations.mapper import UserOrganizationMapper
from src.user_organizations.repository import UserOrganizationRepository
from src.user_organizations.service import UserOrganizationService


def user_organization_service_dependency(session_dependency: Callable[..., Any]) -> Callable[[AsyncSession], UserOrganizationService]:
    def dependency(
        session: Annotated[AsyncSession, Depends(session_dependency)],
    ) -> UserOrganizationService:
        repository = UserOrganizationRepository(session)
        mapper = UserOrganizationMapper()
        return UserOrganizationService(repository, mapper)

    return dependency


get_read_user_organization_service = user_organization_service_dependency(get_read_session)
get_user_organization_service = user_organization_service_dependency(get_session)
