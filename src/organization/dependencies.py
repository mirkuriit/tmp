from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_read_session, get_session
from src.organization.mapper import OrganizationMapper
from src.organization.repository import OrganizationRepository
from src.organization.service import OrganizationService


def organization_service_dependency(session_dependency: Callable[..., Any]) -> Callable[[AsyncSession], OrganizationService]:
    def dependency(
        session: Annotated[AsyncSession, Depends(session_dependency)],
    ) -> OrganizationService:
        repository = OrganizationRepository(session)
        mapper = OrganizationMapper()
        return OrganizationService(repository, mapper)

    return dependency


get_read_organization_service = organization_service_dependency(get_read_session)
get_organization_service = organization_service_dependency(get_session)