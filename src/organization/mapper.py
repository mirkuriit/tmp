from collections.abc import Iterable

from src.organization.model import Organization
from src.organization.schema import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)


class OrganizationMapper:
    @staticmethod
    def schema_to_model(data: OrganizationCreate) -> Organization:
        return Organization(**data.model_dump())

    @classmethod
    def schema_to_model_list(cls, data: Iterable[OrganizationCreate]) -> list[Organization]:
        return [cls.schema_to_model(organization) for organization in data]

    @staticmethod
    def model_to_schema(data: Organization) -> OrganizationResponse:
        return OrganizationResponse.model_validate(data)


    @classmethod
    def model_to_schema_list(cls, data: Iterable[Organization]) -> list[OrganizationResponse]:
        return [cls.model_to_schema(organization) for organization in data]


    @staticmethod
    def update_model_from_schema(data: Organization, updated_data: OrganizationUpdate) -> Organization:
        for field, value in updated_data.model_dump(exclude_unset=True, exclude={"id"}).items():
            setattr(data, field, value)
        return data