from fastapi.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND


class NotFoundException(HTTPException):
    def __init__(
            self,
            detail: str,
            status_code: int = HTTP_404_NOT_FOUND,
    ):
        self.status_code = status_code
        self.detail = detail