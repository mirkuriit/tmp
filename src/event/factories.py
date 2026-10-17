from sqlalchemy.ext.asyncio import AsyncSession

from src.event.repository import EventRepository


class EventRepositoryFactory:
    @staticmethod
    def event_repository(session: AsyncSession) -> EventRepository:
        return EventRepository(session)