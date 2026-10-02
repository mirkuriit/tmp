from uuid import UUID

from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_409_CONFLICT
from fastapi import HTTPException

from src.exceptions import NotFoundException
from src.logger import logger
from src.user_organizations.mapper import UserOrganizationMapper
from src.user_organizations.model import UserOrganization
from src.user_organizations.repository import UserOrganizationRepository
from src.user_organizations.schema import (
    UserOrganizationCreate,
    UserOrganizationResponse,
)


class UserOrganizationService:
    def __init__(
            self, repository:
            UserOrganizationRepository,
            mapper: UserOrganizationMapper
    ) -> None:
        self._mapper = mapper
        self._repository = repository

    async def _get_one(self, user_id: UUID, organization_id: UUID) -> UserOrganization:
        user_organization = await self._repository.get_one_or_none(user_id, organization_id)
        if user_organization is None:
            detail = f"User {user_id} is not connected to organization {organization_id}"
            exception = NotFoundException(detail=detail)
            logger.exception(
                detail,
                exception=exception,
            )
            raise exception
        return user_organization

    async def get_one(self, user_id: UUID, organization_id: UUID) -> UserOrganizationResponse:
        user_organization = await self._get_one(user_id, organization_id)
        return self._mapper.model_to_schema(user_organization)

    async def create(self, data: UserOrganizationCreate) -> UserOrganizationResponse:
        user_organization = await self._repository.create(self._mapper.schema_to_model(data))
        return self._mapper.model_to_schema(user_organization)

    async def create_many(self, data: list[UserOrganizationCreate]) -> list[UserOrganizationResponse]:
        user_organizations = await self._repository.create_many(
            self._mapper.schema_to_model_list(data)
        )
        return self._mapper.model_to_schema_list(user_organizations)

    async def delete(self, user_id: UUID, organization_id: UUID) -> UserOrganizationResponse:
        user_organization = await self._get_one(user_id, organization_id)
        deleted = await self._repository.delete(user_organization)
        return self._mapper.model_to_schema(deleted)
