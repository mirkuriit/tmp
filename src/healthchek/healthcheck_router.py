from fastapi import APIRouter

from src.healthchek.enums import HealthcheckStatus
from src.healthchek.schema import HealthcheckResponse

router = APIRouter()


@router.get('/healthcheck')
async def healthcheck() -> HealthcheckResponse:
    return HealthcheckResponse(status=HealthcheckStatus.OK)
