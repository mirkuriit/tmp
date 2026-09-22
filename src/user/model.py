from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import AuditMixin, Base

if TYPE_CHECKING:
    from src.organization.model import Organization


class UserOrganization(AuditMixin, Base):
    __tablename__ = 'user_organizations'
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), primary_key=True)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey('organizations.id'), primary_key=True)
    user: Mapped["User"] = relationship(back_populates="user_organizations")
    organization: Mapped["Organization"] = relationship(back_populates="organization_users")

    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_user_id_organization_id"),
    )

class User(AuditMixin, Base):
    __tablename__ = 'users'
    username: Mapped[str]
    bio: Mapped[str | None] = mapped_column(String(140), nullable=True)
    has_premium: Mapped[bool] = mapped_column(default=False)
    logo_url: Mapped[str | None] = mapped_column(nullable=True)
    organizations: Mapped[list["Organization"]] = relationship(
        secondary="user_organizations",
        back_populates="users",
        lazy="selectin",
        primaryjoin="User.id == UserOrganization.user_id",
        secondaryjoin="and_(Organization.id == UserOrganization.organization_id, Organization.is_deleted == False)",
    )
    user_organizations: Mapped[list[UserOrganization]] = relationship(
        back_populates="user"
    )