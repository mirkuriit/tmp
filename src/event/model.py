import datetime as dt

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import AuditMixin, Base


class Event(AuditMixin, Base):
    __tablename__ = 'events'
    name: Mapped[str]
    description: Mapped[str]
    start_date: Mapped[dt.datetime] = mapped_column(sa.TIMESTAMP(timezone=True))
    end_date: Mapped[dt.datetime]  = mapped_column(sa.TIMESTAMP(timezone=True))
    event_info: Mapped["EventInfo"] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class EventInfo(AuditMixin, Base):
    __tablename__ = 'event_info'
    organizer: Mapped[str | None] = mapped_column(nullable=True)
    head_url: Mapped[str | None] = mapped_column(nullable=True)
    location: Mapped[str | None] = mapped_column(nullable=True)

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), unique=True)
    event: Mapped[Event] = relationship(back_populates="event_info", single_parent=True)

