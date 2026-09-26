from uuid import UUID

from pydantic import Field

from src.schemas import Base


class EventInfoBase(Base):
    organizer: str | None = None
    head_url: str | None = Field(default=None, examples=["https://example.com/"])
    location: str | None = None


class EventInfoCreate(EventInfoBase):
    pass


class EventInfoUpdate(EventInfoBase):
    pass


class EventInfoResponse(EventInfoBase):
    id: UUID