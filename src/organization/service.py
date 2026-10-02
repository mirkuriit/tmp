from uuid import UUID

from src.exceptions import NotFoundException
from src.logger import logger
from src.organization.mapper import OrganizationMapper
from src.organization.model import Organization
from src.organization.repository import OrganizationRepository
from src.organization.schema import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)


class OrganizationService:
    def __init__(self, repository: OrganizationRepository,
                 mapper: OrganizationMapper) -> None:
        self._mapper = mapper
        self._repository = repository

    async def _get_one(
            self,
            organization_id: UUID,
    ) -> Organization:
        organization = await self._repository.get_one_or_none(organization_id)
        if organization is None:
            detail = f"Organization with id: {organization_id} not found"
            exception = NotFoundException(detail=detail)
            logger.exception(
                detail,
                exception=exception,
            )
            raise exception
        return organization


    async def get_one(self, organization_id: UUID) -> OrganizationResponse:
        organization = await self._get_one(organization_id)
        return self._mapper.model_to_schema(organization)


    async def get_many(self) -> list[OrganizationResponse]:
        return await self._repository.get_many()


    async def create(self, data: OrganizationCreate) -> OrganizationResponse:
        organization = await self._repository.create(self._mapper.schema_to_model(data))
        return self._mapper.model_to_schema(organization)


    async def create_many(self, data: list[OrganizationCreate])-> list[OrganizationResponse]:
        organizations = await self._repository.create_many(self._mapper.schema_to_model_list(data))
        return self._mapper.model_to_schema_list(organizations)


    async def update(self, organization_id: UUID,
                     data: OrganizationUpdate) -> OrganizationResponse:
        organization = await self._get_one(organization_id)
        organization = await self._repository.update(organization, data)
        return self._mapper.model_to_schema(organization)


    async def update_many(self, organization_ids: list[UUID], data: list[OrganizationUpdate]) -> list[OrganizationResponse]:
        updated_organizations = []
        for organization_id in organization_ids:
            for organization_update_schema in data:
                if organization_id == organization_update_schema.id:
                    updated_organizations.append(await self.update(organization_id, organization_update_schema))
        return self._mapper.model_to_schema_list(updated_organizations)


    async def delete(
            self,
            organization_id: UUID,
    ) -> OrganizationResponse:
        organization = await self._get_one(organization_id)
        deleted_organization = await self._repository.delete(organization)
        return self._mapper.model_to_schema(deleted_organization)


    async def delete_many(
            self,
            organization_ids: list[UUID]
    ) -> None:
        for organization_id in organization_ids:
            await self.delete(organization_id)
