import datetime as dt
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import ColumnElement, and_, func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.mapper import UserMapper
from src.user.model import User
from src.user.schema import UserUpdate
from src.utils import string_hash


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self._session = db_session


    async def refresh(self, user: User) -> None:
        await self._session.refresh(user)


    async def get_advisory_lock(self, lock_key: str) -> None:
        await self._session.scalar(
            func.pg_advisory_xact_lock(string_hash(lock_key)))


    async def get_one_or_none(
            self,
            user_id: UUID,
            *,
            is_deleted: bool = False,
    ) -> User | None:
        base_filters = [
            User.id == user_id,
            User.is_deleted == is_deleted
        ]

        return await self._session.scalar(select(User).where(*base_filters))


    async def get_many(
            self,
            limit: int,
            show_after_datetime: dt.datetime | None = None,
            show_after_id: UUID | None = None,
            *,
            filters: list[ColumnElement[bool]] | None = None
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
        if filters:
            statement = statement.where(
                *filters
            )
        return (await self._session.scalars(statement)).all()

    async def create(self, data: User) -> User | None:
        return await self._session.scalar(
            insert(User).values(
                username=data.username,
                bio=data.bio,
                logo_url=data.logo_url,
                has_premium=data.has_premium
            ).on_conflict_do_nothing(
                index_elements=[User.username]
            ).returning(User)
        )


    async def update(self, user: User, updated_schema: UserUpdate) -> User:
        user = UserMapper.update_model_from_schema(user, updated_schema)
        await self._session.flush()
        return user


    async def delete(
            self,
            user: User,
    ) -> User:
        user.is_deleted = True
        await self._session.flush()
        return user

