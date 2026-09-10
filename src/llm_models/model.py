from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import AuditMixin, Base

if TYPE_CHECKING:
    from src.project.model import Project


class LLMModel(AuditMixin, Base):
    __tablename__ = 'llm_models'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    description: Mapped[str | None] = mapped_column(nullable=True)
    base_api_url: Mapped[str]
    token_cost: Mapped[Decimal] = mapped_column(Numeric(21, 4), default=0)

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="llm_models",
    )