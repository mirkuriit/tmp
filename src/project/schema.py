from uuid import UUID

from src.schemas import Base


class ProjectBase(Base):
    name: str
    description: str


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: UUID
    likes: int


class ProjectUpdate(ProjectBase):
    name: str | None
    description: str | None



