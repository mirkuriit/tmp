import datetime as dt
from uuid import UUID

from sqlalchemy import Sequence, and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.user.mapper import UserMapper
from src.user.model import User
from src.user.schema import UserUpdate


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def get_one_or_none(
            self,
            user_id: UUID,
            *,
            is_deleted: bool = False,
    ):
        filters = [
            User.id == user_id,
            User.is_deleted == is_deleted
        ]

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

    async def create(self, user: User) -> User:
        self._session.add(user)
        await self._session.flush()
        return user

    async def update(self, user: User, updated_schema: UserUpdate):
        user = UserMapper.update_model_from_schema(user, updated_schema)
        await self._session.flush()
        return user

    async def delete(self, user: User,
                     organization_id: UUID | None = None) -> User:
        if user and organization_id is None:
            user.is_deleted = True
        for model in user.organizations:
            if model.id == organization_id or organization_id is None:
                model.is_deleted = True
        await self._session.flush()
        return user

