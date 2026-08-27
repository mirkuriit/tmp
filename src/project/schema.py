from uuid import UUID

from src.schemas import Base


class ProjectCreate(Base):
    id: UUID
    name: str
    description: str


class ProjectGetOne(Base):
    id: UUID
    name: str
    description: str
    likes: int


class ProjectUpdate(Base):
    name: str | None
    description: str | None



