from fastapi.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND


class ProjectNotFoundException(HTTPException):
    def __init__(
            self,
            status_code: int = HTTP_404_NOT_FOUND,
            detail: str = "Project not found"
    ):
        self.status_code = status_code
        self.detail = detail