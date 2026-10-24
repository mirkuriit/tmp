from typing import TypeVar
import asyncio
import datetime as dt
import httpx
import random
from fastapi import HTTPException
from httpx import TimeoutException, ConnectError

from pydantic import BaseModel
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND, HTTP_502_BAD_GATEWAY, \
    HTTP_429_TOO_MANY_REQUESTS, HTTP_500_INTERNAL_SERVER_ERROR

T = TypeVar("T", bound=BaseModel)


class RetryBudget:
    def __init__(self, allowed_retries_percentage: float) -> None:
        self._last_minute_requests_total = 0
        self._last_minute_retries_total = 0
        self._start_minute_time = dt.datetime.now()
        self._allowed_retries_percentage = allowed_retries_percentage

    def _reset_last_minute_requests_total(self):
        self._last_minute_requests_total = 0
        self._last_minute_retries_total = 0
        self._start_minute_time = dt.datetime.now()

    def _try_reset_last_minute_requests_total(self):
        if (dt.datetime.now() - self._start_minute_time).seconds >= 60:
            self._reset_last_minute_requests_total()

    def add_request(self):
        self._try_reset_last_minute_requests_total()
        self._last_minute_requests_total += 1

    def add_retry(self):
        self._try_reset_last_minute_requests_total()
        self._last_minute_retries_total += 1

    def can_retry(self) -> bool:
        return self._last_minute_retries_total <= self._allowed_retries_percentage * self._last_minute_requests_total

class HTTPClient:
    def __init__(self, client: httpx.AsyncClient, max_retry_count: int, max_delay_ms: int, delay_base_ms, retry_budget: RetryBudget) -> None:
        self._client = client
        self._MAX_RETRY_COUNT = max_retry_count
        self._MAX_DELAY_MS = max_delay_ms
        self._DELAY_BASE_MS = delay_base_ms
        self._retry_budget = retry_budget

    async def sleep_for_retry(self, attempt_count: int) -> None:
        delay = min(self._DELAY_BASE_MS * pow(2, attempt_count),
                    self._MAX_DELAY_MS) / 1000
        await asyncio.sleep(delay + random.uniform(0, delay))

    async def get(self, *args, **kwargs) -> httpx.Response:
        self._retry_budget.add_request()
        attempt_count = 0
        while True:
            attempt_count += 1
            try:
                response =  await self._client.get(*args, **kwargs)
            except (TimeoutException, ConnectError):
                if self._retry_budget.can_retry() and attempt_count < self._MAX_RETRY_COUNT:
                    self._retry_budget.add_retry()
                    await self.sleep_for_retry(attempt_count)
                    continue
                else:
                    break

            if response.is_success:
                return response
            if response.status_code == HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND)
            if response.status_code < HTTP_500_INTERNAL_SERVER_ERROR and response.status_code != HTTP_429_TOO_MANY_REQUESTS:
                raise HTTPException(
                    status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )

            if self._retry_budget.can_retry() and attempt_count < self._MAX_RETRY_COUNT:
                self._retry_budget.add_retry()
                await self.sleep_for_retry(attempt_count)
            else:
                break

        raise HTTPException(
            status_code=HTTP_502_BAD_GATEWAY,
            detail="The external service sent an invalid response."
        )

    async def post(self, *args, **kwargs)-> httpx.Response:
        try:
            response = await self._client.post(*args, **kwargs)
            return response
        except (TimeoutException, ConnectError) as ex:
            raise HTTPException(
                status_code=HTTP_502_BAD_GATEWAY,
                detail=str(ex)
            )


    async def get_response(self, response_model: type[T], *args, **kwargs, ) -> T :
        response = await self.get(*args, **kwargs)
        return response_model.model_validate(response.json())

    async def post_response(self, response_model: type[T], *args, **kwargs) -> T :
        response = await self.post(*args, **kwargs)
        return response_model.model_validate(response.json())


def http_client_dependency(request: Request) -> HTTPClient:
    return request.app.state.http_client
