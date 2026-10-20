from copy import deepcopy
from typing import Any
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)

from tests.utils import compare_dict_fields


@pytest.fixture(scope="session")
def create_user_body() -> dict[str, Any]:
    return {
        "username": "user",
        "bio": "string",
        "logo_url": "https://example.com/",
        "has_premium": True,
        "organizations": [
            {
                "name": "organization",
                "description": "string",
                "logo_url": "https://example.com/"
            }
        ]
    }


@pytest.fixture(scope="session")
def update_user_body() -> dict[str, Any]:
    return {
        "username": "updated string",
        "bio": "I tried so hard to write fucking tests. "
               "But in the end it doesn't even matter",
    }


@pytest.fixture(scope="session", autouse=True)
async def created_user_id(client: AsyncClient,
                          create_user_body: dict[str, Any]) -> str:
    response = await client.post(
        "/user/v1",
        json=create_user_body
    )

    assert response.status_code == HTTP_201_CREATED
    user_id = response.json().get("id")
    assert user_id is not None and isinstance(user_id, str) and isinstance(
        UUID(user_id), UUID)
    return user_id


async def test_create_user_with_exists_username(
        client: AsyncClient,
        create_user_body: dict[str, Any],
):
    response = await client.post(
        "/user/v1",
        json=create_user_body
    )

    assert response.status_code == HTTP_409_CONFLICT


async def test_get_exists_user(
        created_user_id: UUID,
        client: AsyncClient,
        create_user_body: dict[str, Any]
):
    response = await client.get(
        f"/user/v1/{created_user_id}",
    )

    assert response.status_code == HTTP_200_OK
    compare_dict_fields(
        response.json(), create_user_body,
        exclude={"organizations"}
    )
    assert len(response.json()["organizations"]) == len(
        create_user_body["organizations"]
    )
    compare_dict_fields(
        response.json()["organizations"][0], create_user_body["organizations"][0]
    )


async def test_get_not_exists_user(
        client: AsyncClient,
):
    response = await client.get(
        f"/user/v1/{uuid4()}",
    )

    assert response.status_code == HTTP_404_NOT_FOUND


async def test_update_user_with_exists_username(
        created_user_id: UUID,
        client: AsyncClient,
        update_user_body: dict[str, Any],
        create_user_body: dict[str, Any]
):
    modified_create_user_body = deepcopy(create_user_body)
    modified_create_user_body["username"] = "somename"
    response = await client.post(
        "/user/v1",
        json=modified_create_user_body
    )
    assert response.status_code == HTTP_201_CREATED
    assert response.json()["username"] == modified_create_user_body["username"]
    user_id_for_delete_after_test = response.json().get("id")

    response = await client.patch(
        f"/user/v1/{created_user_id}",
        json={"username": modified_create_user_body["username"]}
    )
    assert response.status_code == HTTP_409_CONFLICT

    response = await client.delete(
        f"/user/v1/{user_id_for_delete_after_test}",
    )
    assert response.status_code == HTTP_204_NO_CONTENT


async def test_update_exists_user(
        created_user_id: UUID,
        client: AsyncClient,
        update_user_body: dict[str, Any],
):
    response = await client.patch(
        f"/user/v1/{created_user_id}",
        json=update_user_body
    )
    assert response.status_code == HTTP_200_OK
    compare_dict_fields(response.json(), update_user_body, only_include={"username", "bio"})

    response = await client.get(
        f"/user/v1/{created_user_id}",
    )
    assert response.status_code == HTTP_200_OK
    compare_dict_fields(response.json(), update_user_body)


async def test_update_not_exists_user(
        created_user_id: UUID,
        client: AsyncClient,
        update_user_body: dict[str, Any],
):
    response = await client.patch(
        f"/user/v1/{uuid4()}",
        json={"bio": update_user_body["bio"]}
    )
    assert response.status_code == HTTP_404_NOT_FOUND


async def test_delete_exists_user(
        created_user_id: UUID,
        client: AsyncClient,
        update_user_body: dict[str, Any],
):
    response = await client.delete(
        f"/user/v1/{created_user_id}",
    )
    assert response.status_code == HTTP_204_NO_CONTENT

    response = await client.get(
        f"/user/v1/{created_user_id}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND


async def test_delete_not_exists_user(
        created_user_id: UUID,
        client: AsyncClient,
        update_user_body: dict[str, Any],
):
    response = await client.delete(
        f"/user/v1/{uuid4()}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND


async def test_get_users(
        created_user_id: UUID,
        client: AsyncClient,
        create_user_body: dict[str, Any]
):
    user_count = 10
    first_users_pack = 7
    second_users_pack_limit = 3

    body = deepcopy(create_user_body)
    for i in range(user_count):
        body["username"] = f"name #{i}"
        response = await client.post(
            "/user/v1",
            json=body
        )
        assert response.status_code == HTTP_201_CREATED

    response = await client.get(
        "/user/v1/",
        params={
            "limit": first_users_pack,
        }
    )
    assert response.status_code == HTTP_200_OK
    assert len(response.json()["items"]) == first_users_pack
    for i, item in enumerate(response.json()["items"]):
        assert item["username"] == f"name #{i}"

    response = await client.get(
        "/user/v1/",
        params={
            "show_after_datetime": response.json().get("last_seen_datetime"),
            "show_after_id": response.json().get("last_seen_id"),
        }
    )

    assert response.status_code == HTTP_200_OK
    for i, item in enumerate(response.json()["items"]):
        assert item["username"] == f"name #{i + first_users_pack}"
    assert len(response.json()["items"]) == second_users_pack_limit
