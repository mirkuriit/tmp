import datetime as dt
from typing import TypeVar, Any
from uuid import UUID

import redis.asyncio as redis
from pydantic import BaseModel
from redis import ResponseError
from starlette.requests import Request

T = TypeVar("T", bound=BaseModel)


class CacheClient:
    def __init__(self, client: redis.Redis, default_cache_key_ttl: int):
        self._client = client
        self.default_cache_key_ttl = default_cache_key_ttl

    @staticmethod
    def get_one_cache_key(id_: UUID, key: str) -> str:
        return f"{key}:{id_}"

    async def update_get_many_cache_key_version(self, table_name: str) -> int:
        cache_key = f"{table_name}:version"
        try:
            return await self._client.incr(cache_key)
        except ResponseError:
            await self._client.set(cache_key, 1)
            return 1

    async def get_many_cache_key(
            self,
            table_name: str,
            show_after_datetime: dt.datetime | None,
            show_after_id: UUID | None,
            limit: int
    ) -> str:
        key_version = await self._client.get(f"{table_name}:version")
        return f"{table_name}:v{key_version}:{show_after_id}:{show_after_datetime}:{limit}"

    async def get(self, key: str):
        return await self._client.get(key)

    async def set(self, key: str, value: Any):
        return await self._client.set(key, value)

    async def get_response(self, key: str, model: type[T]) -> T | None:
        result = await self._client.get(key)

        if result is None:
            return None

        return model.model_validate_json(result)

    async def set_response(
        self,
        key: str,
        data: BaseModel,
    ) -> bool:
        return await self._client.set(
            key,
            data.model_dump_json(),
            ex=self.default_cache_key_ttl
        )

    async def delete(self, key: str):
        return await self._client.delete(key)



def get_cache_client(request: Request) -> CacheClient:
    return request.app.state.cache_client