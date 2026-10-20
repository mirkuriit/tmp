from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import AuditMixin, Base

if TYPE_CHECKING:
    from src.organization.model import Organization
    from src.user_organizations.model import UserOrganization


class User(AuditMixin, Base):
    __tablename__ = 'users'
    username: Mapped[str] = mapped_column(unique=True)
    bio: Mapped[str | None] = mapped_column(String(140), nullable=True)
    has_premium: Mapped[bool] = mapped_column(default=False)
    logo_url: Mapped[str | None] = mapped_column(nullable=True)
    organizations: Mapped[list["Organization"]] = relationship(
        secondary="user_organizations",
        back_populates="users",
        lazy="selectin",
        viewonly=True,
        primaryjoin="User.id == UserOrganization.user_id",
        secondaryjoin="and_(Organization.id == UserOrganization.organization_id, Organization.is_deleted == False)",
    )
    user_organizations: Mapped[list["UserOrganization"]] = relationship(
        back_populates="user"
    )