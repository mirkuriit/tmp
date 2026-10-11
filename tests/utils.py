from typing import Any

from src.logger import logger


def compare_object_fields(
        obj1: Any,
        obj2: Any,
        *,
        exclude: set[str] | None = None
)-> None:
    attributes = (set(vars(obj1)) & set(vars(obj2)))
    logger.info(f"Attributes: {attributes}")
    for attribute in attributes:
        if exclude is None or attribute not in exclude:
            logger.info(f"obj1: {getattr(obj1, attribute)} | obj2: {getattr(obj2, attribute)}")
            assert getattr(obj1, attribute) == getattr(obj2, attribute)