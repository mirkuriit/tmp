import hashlib


def import_models():
    from src.event.model import Event, EventInfo  # noqa: F401
    from src.llm_models.model import LLMModel  # noqa: F401
    from src.organization.model import Organization  # noqa: F401
    from src.project.model import Project  # noqa: F401
    from src.user.model import User, UserOrganization  # noqa: F401


def string_hash(string: str) -> int:
    return int.from_bytes(
        hashlib.blake2b(
            string.encode(),
            digest_size=8
        ).digest(),
        "big",
        signed=True
    )
