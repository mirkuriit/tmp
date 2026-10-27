import datetime as dt
from enum import StrEnum
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.event_info.model import EventInfo
from src.models import AuditMixin, Base


class ModerationDecisionStatus(StrEnum):
    NEW = "new"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Event(AuditMixin, Base):
    __tablename__ = 'events'
    name: Mapped[str]
    description: Mapped[str]
    start_date: Mapped[dt.datetime] = mapped_column(sa.TIMESTAMP(timezone=True))
    end_date: Mapped[dt.datetime]  = mapped_column(sa.TIMESTAMP(timezone=True))
    moderation_decision_id: Mapped[UUID | None]
    moderation_decision_status: Mapped[ModerationDecisionStatus] = mapped_column(
        Enum(
            ModerationDecisionStatus,
            name="moderation_decision_status_enum",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=ModerationDecisionStatus.NEW,
    )
    event_info: Mapped[EventInfo] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


