from enum import Enum


class HealthcheckStatus(Enum):
    OK = "OK"
    DEAD = "DEAD"