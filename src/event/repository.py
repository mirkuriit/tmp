import datetime as dt
from uuid import UUID

from sqlalchemy import Sequence, and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.event.mapper import EventMapper
from src.event.model import Event
from src.event.schema import EventUpdate


class EventRepository:
    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def get_one_or_none(
            self,
            event_id: UUID,
            *,
            is_deleted: bool = False,
    ) -> Event | None:
        filters = [
            Event.id == event_id,
            Event.is_deleted == is_deleted
        ]

        return await self._session.scalar(select(Event).where(*filters))

    async def get_many(
            self,
            show_after_datetime: dt.datetime | None,
            show_after_id: UUID | None,
            limit: int
    ) -> Sequence[Event]:
        statement = select(
            Event
        ).order_by(
            Event.created_at,
            Event.id
        ).limit(
            limit
        ).where(
            Event.is_deleted == False
        )
        if show_after_datetime and show_after_id:
            statement = statement.where(
                or_(
                    Event.created_at > show_after_datetime,
                    and_(
                        Event.created_at == show_after_datetime,
                        Event.id > show_after_id
                    )
                )
            )

        return (await self._session.scalars(statement)).all()


    async def create(self, event: Event) -> Event:
        self._session.add(event)
        await self._session.flush()
        return event


    async def update(self, event: Event, updated_schema: EventUpdate) -> Event:
        event = EventMapper.update_model_from_schema(event, updated_schema)
        await self._session.flush()
        return event


    async def delete(self, event: Event) -> Event:
        event.is_deleted = True
        event.event_info.is_deleted = True
        await self._session.flush()
        return event

