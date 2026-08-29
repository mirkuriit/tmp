import uuid

from fastapi import Request
from fastapi.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from src.logger import conntext_correlation_id, context_request_info, logger

class LogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
        request_url = request.url.path
        method = request.method

        conntext_correlation_id_token = conntext_correlation_id.set(correlation_id)
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
            return response
        except Exception as ex:
            exception = str(ex)
            request_info["exception"] = exception
            request_info["status_code"] = 500
            raise
        finally:
            logger.info("http_request")
            context_request_info.reset(request_token)
            conntext_correlation_id.reset(conntext_correlation_id_token)
