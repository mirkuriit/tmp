from typing import Any

import sqlalchemy as sa
from sqlalchemy import Sequence

from src.user.model import User
from src.user.schema import PaginatedUserResponse, UserCreate, UserResponse, UserUpdate


class UserMapper:
    DEFAULT_FIELDS = frozenset({"created_at", "updated_at", "is_deleted", "id"})

    @staticmethod
    def schema_to_model(data: UserCreate) -> User:
        return User(**data.model_dump(exclude={"organizations"}))

    @staticmethod
    def model_to_schema(data: User) -> UserResponse:
        return UserResponse.model_validate(data)

    @staticmethod
    def models_to_pagination_schema(users: Sequence[User]) -> PaginatedUserResponse:
        if not users:
            return PaginatedUserResponse(
                items=users,
                last_seen_id=None,
                last_seen_datetime=None
            )
        return PaginatedUserResponse(
            items=users,
            last_seen_id=users[-1].id,
            last_seen_datetime=users[-1].created_at
        )

    @classmethod
    def model_to_dict(cls, data: User) -> dict[str, Any]:
        return {attr.key: getattr(data, attr.key) for attr in sa.inspect(data).mapper.column_attrs if attr.key not in cls.DEFAULT_FIELDS}


    @staticmethod
    def update_model_from_schema(data: User, updated_data: UserUpdate) -> User:
        for field, value in updated_data.model_dump(exclude_unset=True, exclude={"organizations"}).items():
            setattr(data, field, value)

        return data