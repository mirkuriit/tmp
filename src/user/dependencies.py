from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from src.cache import CacheClient, get_cache_client
from src.user.factories import UserRepositoryFactory, UserServiceFactory
from src.user.mapper import UserMapper
from src.user.service import UserService
from src.user.unit_of_work import UserUOW


def user_service_dependency(request: Request, cache_client: Annotated[CacheClient, Depends(get_cache_client)]) -> UserService:
    user_mapper = UserMapper()
    user_cache_client = cache_client
    user_service_factory = UserServiceFactory()
    user_repository_factory = UserRepositoryFactory()
    user_uow = UserUOW(request.app.state.SessionFactory, user_service_factory, user_repository_factory)

    return UserService(
        user_mapper,
        user_cache_client,
        user_uow
    )


get_user_service = user_service_dependency