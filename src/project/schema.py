from typing import Optional
from uuid import UUID

from src.schemas import Base


class ProjectBase(Base):
    name: str
    description: Optional[str | None] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: UUID
    likes: int


class ProjectUpdate(ProjectBase):
    name: Optional[str | None] = None



