from src.user_organizations.model import UserOrganization
from src.user_organizations.schema import (
    UserOrganizationCreate,
    UserOrganizationResponse,
)


class UserOrganizationMapper:
    @staticmethod
    def schema_to_model(data: UserOrganizationCreate) -> UserOrganization:
        return UserOrganization(**data.model_dump())

    @classmethod
    def schema_to_model_list(cls, data: list[UserOrganizationCreate]) -> list[UserOrganization]:
        return [cls.schema_to_model(user_organization) for user_organization in data]

    @staticmethod
    def model_to_schema(data: UserOrganization) -> UserOrganizationResponse:
        return UserOrganizationResponse.model_validate(data)

    @classmethod
    def model_to_schema_list(cls, data: list[UserOrganization]  ) -> list[UserOrganizationResponse]:
        return [cls.model_to_schema(user_organization) for user_organization in data]
