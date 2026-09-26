import datetime as dt
from uuid import UUID

from sqlalchemy import Sequence, and_, func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import ResourceIsLockedException
from src.organization.model import Organization
from src.user.mapper import UserMapper
from src.user.model import User, UserOrganization
from src.user.schema import UserCreate, UserUpdate
from src.utils import string_hash


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def get_advisory_lock(self, key: int)-> bool:
        return not(
                await self._session.scalar(
                    func.pg_try_advisory_xact_lock(key)
                )
            )


    async def get_one_or_none(
            self,
            user_id: UUID,
            *,
            need_advisory_lock: bool = False,
            is_deleted: bool = False,
    ) -> User | None:
        filters = [
            User.id == user_id,
            User.is_deleted == is_deleted
        ]
        if need_advisory_lock:
            is_blocked = await self.get_advisory_lock(
                string_hash(f"{User.__tablename__}:{user_id}")
            )
            if is_blocked:
                raise ResourceIsLockedException
        return await self._session.scalar(select(User).where(*filters))


    async def get_many(
            self,
            show_after_datetime: dt.datetime | None,
            show_after_id: UUID | None, limit: int
    ) -> Sequence[User]:
        statement = select(
            User
        ).order_by(
            User.created_at,
            User.id
        ).limit(
            limit
        ).where(
            User.is_deleted == False
        )
        if show_after_datetime and show_after_id:
            statement = statement.where(
                or_(
                    User.created_at > show_after_datetime,
                    and_(
                        User.created_at == show_after_datetime,
                        User.id > show_after_id
                    )
                )
            )

        return (await self._session.scalars(statement)).all()

    async def create(self, data: UserCreate) -> User:
        user = await self._session.scalar(insert(User).values(**data.model_dump(exclude={"organizations"})).returning(User))
        for organization in data.organizations:
            organization = await self._session.scalar(insert(Organization).values(**organization.model_dump(exclude={"users"})).returning(Organization))
            await self._session.execute(insert(UserOrganization).values(user_id=user.id, organization_id=organization.id).on_conflict_do_nothing())
        await self._session.refresh(user)
        return user

    async def update(self, user: User, updated_schema: UserUpdate) -> User:
        user = UserMapper.update_model_from_schema(user, updated_schema)
        await self._session.flush()
        return user

    async def delete(
            self,
            user: User,
            organization_id: UUID | None = None
    ) -> User:
        if user and organization_id is None:
            user.is_deleted = True
        for model in user.organizations:
            if model.id == organization_id or organization_id is None:
                model.is_deleted = True
        await self._session.flush()
        return user

