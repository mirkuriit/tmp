from src.healthchek.enums import HealthcheckStatus
from src.schemas import BaseModel


class HealthcheckResponse(BaseModel):
    status: HealthcheckStatus


