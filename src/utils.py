def import_models():
    from src.event.model import Event, EventInfo  # noqa: F401
    from src.llm_models.model import LLMModel  # noqa: F401
    from src.project.model import Project  # noqa: F401
    from src.user.model import Organization, User, UserOrganization  # noqa: F401
