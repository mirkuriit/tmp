from typing import Any


def compare_object_fields(
        obj1: Any,
        obj2: Any,
        *,
        exclude: set[str] | None = None
):
    attributes = (set(vars(obj1)) & set(vars(obj2)))
    for attribute in attributes:
        if exclude and attribute not in exclude:
            assert getattr(obj1, attribute) == getattr(obj2, attribute)