from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column

from src.models import AuditMixin, Base


class Project(AuditMixin, Base):
    __tablename__ = 'projects'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    description: Mapped[str] = mapped_column(nullable=True)
    likes: Mapped[int] = mapped_column(default=0)