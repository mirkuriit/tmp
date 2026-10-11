from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.user_organizations.model import UserOrganization


class UserOrganizationRepository:
    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def get_one_or_none(
            self,
            user_id: UUID,
            organization_id: UUID,
            *,
            is_deleted: bool = False,
    ) -> UserOrganization | None:
        statement = select(UserOrganization).where(
            UserOrganization.user_id == user_id,
            UserOrganization.organization_id == organization_id,
            UserOrganization.is_deleted == is_deleted,
        )
        return await self._session.scalar(statement)


    async def get_by_user_id(
            self,
            user_id: UUID
    ) -> Sequence[UserOrganization]:
        statement = select(
            UserOrganization
        ).where(
            UserOrganization.is_deleted == False,
            UserOrganization.user_id == user_id
        )

        return (await self._session.scalars(statement)).all()


    async def create(self, user_organization: UserOrganization) -> UserOrganization:
        self._session.add(user_organization)
        await self._session.flush()
        return user_organization


    async def create_many(self, user_organizations: list[UserOrganization]) -> list[UserOrganization]:
        self._session.add_all(user_organizations)
        await self._session.flush()
        return user_organizations


    async def delete_many(self, user_organizations: list[UserOrganization]) -> list[UserOrganization]:
        for user_organization in user_organizations:
            user_organization.is_deleted = True
        await self._session.flush()
        return user_organizations
