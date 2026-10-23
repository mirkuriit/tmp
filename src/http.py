from typing import TypeVar

import httpx
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class HTTPClient:
    # TODO (egor): обработка всяких ошибок 404, 500
    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    async def get(self, *args, **kwargs) :
        return await self._client.get(*args, **kwargs)

    async def post(self, *args, **kwargs) :
        return await self._client.post(*args, **kwargs)

    async def get_response(self, response_model: type[T], *args, **kwargs, ) :
        response = await self._client.get(*args, **kwargs)
        return response_model.model_validate(response.json())

    async def post_response(self, response_model: type[T], *args, **kwargs) :
        response = await self._client.post(*args, **kwargs)
        return response_model.model_validate(response.json())





async def http_client_dependency() -> HTTPClient:
    async with httpx.AsyncClient() as client:
        yield HTTPClient(client)