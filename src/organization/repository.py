from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.organization.mapper import OrganizationMapper
from src.organization.model import Organization
from src.organization.schema import OrganizationUpdate


class OrganizationRepository:
    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def get_one_or_none(
            self,
            organization_id: UUID,
            *,
            is_deleted: bool = False,
    ) -> Organization | None:
        filters = [
            Organization.id == organization_id,
            Organization.is_deleted == is_deleted
        ]
        return await self._session.scalar(select(Organization).where(*filters))


    async def get_many(
            self,
    ) -> Sequence[Organization]:
        statement = select(
            Organization
        ).where(
            Organization.is_deleted == False
        )

        return (await self._session.scalars(statement)).all()

    async def create(self, organization: Organization) -> Organization:
        self._session.add(organization)
        await self._session.flush()
        return organization

    async def create_many(self, organizations: list[Organization]) -> list[Organization]:
        self._session.add_all(organizations)
        await self._session.flush()
        return organizations

    async def update(self, organization: Organization, updated_schema: OrganizationUpdate) -> Organization:
        organization = OrganizationMapper.update_model_from_schema(organization, updated_schema)
        await self._session.flush()
        return organization

    async def delete(
            self,
            organization: Organization,
    ) -> Organization:
        organization.is_deleted = True
        await self._session.flush()
        return organization