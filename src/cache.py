
from typing import TypeVar

import redis.asyncio as redis
from pydantic import BaseModel
from starlette.requests import Request

T = TypeVar("T", bound=BaseModel)

class CacheClient:
    DEFAULT_KEY_TTL = 30
    def __init__(self, client: redis.Redis):
        self._client = client

    async def get(self, key: str, model: type[T]) -> T | None:
        result = await self._client.get(key)

        if result is None:
            return None

        return model.model_validate_json(result)

    async def set(
        self,
        key: str,
        data: BaseModel,
    ) -> bool:
        return await self._client.set(
            key,
            data.model_dump_json(),
            ex=self.DEFAULT_KEY_TTL
        )

def get_cache_client(request: Request) -> CacheClient:
    return request.app.state.cache_client