import datetime as dt
from typing import Annotated
from uuid import UUID

from fastapi import Query

from src.schemas import PaginationPage


def pagination_page_dependency(
        show_after_datetime: dt.datetime | None = None,
        show_after_id: UUID | None = None,
        limit: Annotated[int, Query(ge=1, le=200)] = 10
) -> PaginationPage:
    return PaginationPage(
        show_after_datetime=show_after_datetime,
        show_after_id=show_after_id,
        limit=limit,
    )