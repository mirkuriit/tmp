from typing import Any


def compare_object_fields(
        obj1: Any,
        obj2: Any,
        *,
        exclude: set[str] | None = None,
        only_include: set[str] | None = None
)-> None:
    attributes = (set(vars(obj1)) & set(vars(obj2)))
    if only_include:
        attributes = attributes & only_include
    for attribute in attributes:
        if exclude is None or attribute not in exclude:
            assert getattr(obj1, attribute) == getattr(obj2, attribute)


def compare_dict_fields(
        obj1: dict[str, Any],
        obj2: dict[str, Any],
        *,
        exclude: set[str] | None = None,
        only_include: set[str] | None = None
)-> None:
    attributes = set(obj1.keys()) & set(obj2.keys())
    if only_include:
        attributes = attributes & only_include
    for attribute in attributes:
        if exclude is None or attribute not in exclude:
            assert obj1[attribute] == obj2[attribute]