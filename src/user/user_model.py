from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column

from src.models.base_models import AuditMixin, Base


class UserModel(AuditMixin, Base):
    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str]

