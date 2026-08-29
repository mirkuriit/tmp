import uuid

from fastapi import Request
from fastapi.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from src.logger import context_correlation_id, context_request_info, logger

class LogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
        request_url = request.url.path
        method = request.method

        conntext_correlation_id_token = context_correlation_id.set(correlation_id)
        request_token = context_request_info.set(
            {
                "method": method,
                "request_url": request_url,
            }
        )
        request_info = context_request_info.get()
        try:
            response = await call_next(request)
            status_code = response.status_code
            request_info["status_code"] = status_code
            response.headers["x-correlation-id"] = correlation_id
            logger.info("http_request")
            return response
        except Exception as ex:
            request_info["status_code"] = 500
            logger.exception("Something was wrong", exception=str(ex))
            raise
        finally:
            context_request_info.reset(request_token)
            context_correlation_id.reset(conntext_correlation_id_token)
