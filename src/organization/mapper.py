
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

    @staticmethod
    def model_to_schema(data: Organization) -> OrganizationResponse:
        return OrganizationResponse.model_validate(data)


    @staticmethod
    def update_model_from_schema(data: Organization, updated_data: OrganizationUpdate) -> Organization:
        for field, value in updated_data.model_dump(exclude_unset=True).items():
            setattr(data, field, value)
        return data