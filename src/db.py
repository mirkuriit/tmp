from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


async def get_read_session(request: Request) -> Callable:
    async with request.app.state.SessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_session(request: Request) -> Callable:
    async with request.app.state.SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        self._transaction = await self.session.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self._transaction.__aexit__(
                exc_type,
                exc_val,
                exc_tb,
            )
        finally:
            await self.session.close()


SessionDependency = Annotated[AsyncSession, Depends(get_session)]


def uow_dependency(session: SessionDependency) -> UnitOfWork:
    return UnitOfWork(session)