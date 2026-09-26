from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import AuditMixin, Base

if TYPE_CHECKING:
    from src.event.model import Event

class EventInfo(AuditMixin, Base):
    __tablename__ = 'event_info'
    organizer: Mapped[str]
    head_url: Mapped[str]
    location: Mapped[str]

    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), unique=True)
    event: Mapped["Event"] = relationship(back_populates="event_info", single_parent=True)