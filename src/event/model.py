import datetime as dt
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.event_info.model import EventInfo
from src.models import AuditMixin, Base


class Event(AuditMixin, Base):
    __tablename__ = 'events'
    name: Mapped[str]
    description: Mapped[str]
    start_date: Mapped[dt.datetime] = mapped_column(sa.TIMESTAMP(timezone=True))
    end_date: Mapped[dt.datetime]  = mapped_column(sa.TIMESTAMP(timezone=True))
    moderation_decision_id: Mapped[UUID | None]
    event_info: Mapped[EventInfo] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


