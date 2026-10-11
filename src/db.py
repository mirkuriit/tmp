from collections.abc import Callable

from starlette.requests import Request


async def get_session(request: Request) -> Callable:
    async with request.app.state.SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise



async def get_read_session(request: Request) -> Callable:
    async with request.app.state.SessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
