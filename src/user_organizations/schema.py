from uuid import UUID

from src.schemas import Base


class UserOrganizationBase(Base):
    user_id: UUID
    organization_id: UUID


class UserOrganizationCreate(UserOrganizationBase):
    pass


class UserOrganizationResponse(UserOrganizationBase):
    pass
