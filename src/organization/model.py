from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import AuditMixin, Base

if TYPE_CHECKING:
    from src.user.model import User
    from src.user_organizations.model import UserOrganization

class Organization(AuditMixin, Base):
    __tablename__ = 'organizations'
    name: Mapped[str]
    description: Mapped[str | None] = mapped_column(nullable=True)
    logo_url: Mapped[str | None] = mapped_column(nullable=True)
    users: Mapped[list["User"]] = relationship(
        secondary="user_organizations",
        back_populates="organizations",
        viewonly = True,
    )

    organization_users: Mapped[list["UserOrganization"]] = relationship(
        back_populates="organization"
    )