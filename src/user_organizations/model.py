from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import AuditMixin, Base

if TYPE_CHECKING:
    from src.organization.model import Organization
    from src.user.model import User


class UserOrganization(AuditMixin, Base):
    __tablename__ = 'user_organizations'
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), primary_key=True)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey('organizations.id'), primary_key=True)
    user: Mapped["User"] = relationship(back_populates="user_organizations")
    organization: Mapped["Organization"] = relationship(back_populates="organization_users")

    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_user_id_organization_id"),
    )
