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
)

from tests.utils import compare_dict_fields


@pytest.fixture(scope="session")
def create_project_body() -> dict[str, Any]:
    return {
        "name": "project",
        "allow_experimental_functions": True,
        "description": "string",
        "logo_url": "https://example.com/",
        "llm_models": [
            {
                "name": "llm model",
                "description": "string",
                "base_api_url": "https://example.com/",
                "token_cost": "0.1"
            }
        ]
    }


@pytest.fixture(scope="session")
def update_project_body() -> dict[str, Any]:
    return {
        "name": "updated string",
        "description": "updated descr",
    }


@pytest.fixture(scope="session", autouse=True)
async def created_project_id(client: AsyncClient,
                             create_project_body: dict[str, Any]) -> str:
    response = await client.post(
        "/project/v1",
        json=create_project_body
    )

    assert response.status_code == HTTP_201_CREATED
    project_id = response.json().get("id")
    assert project_id is not None and isinstance(project_id, str) and isinstance(
        UUID(project_id), UUID)
    return project_id


async def test_get_exists_project(
        created_project_id: UUID,
        client: AsyncClient,
        create_project_body: dict[str, Any]
):
    response = await client.get(
        f"/project/v1/{created_project_id}",
    )

    assert response.status_code == HTTP_200_OK
    compare_dict_fields(
        response.json(), create_project_body,
        only_include={
            "name", "description", "logo_url", "allow_experimental_functions"
        }
    )
    assert len(response.json()["llm_models"]) == len(
        create_project_body["llm_models"]
    )
    compare_dict_fields(
        response.json()["llm_models"][0], create_project_body["llm_models"][0],
        only_include={"name", "description", "base_api_url"}
    )


async def test_get_not_exists_project(
        client: AsyncClient,
):
    response = await client.get(
        f"/project/v1/{uuid4()}",
    )

    assert response.status_code == HTTP_404_NOT_FOUND


async def test_update_exists_project(
        created_project_id: UUID,
        client: AsyncClient,
        update_project_body: dict[str, Any],
):
    response = await client.patch(
        f"/project/v1/{created_project_id}",
        json=update_project_body
    )
    assert response.status_code == HTTP_200_OK
    compare_dict_fields(response.json(), update_project_body)

    response = await client.get(
        f"/project/v1/{created_project_id}",
    )
    assert response.status_code == HTTP_200_OK
    compare_dict_fields(response.json(), update_project_body)


async def test_update_not_exists_project(
        created_project_id: UUID,
        client: AsyncClient,
        update_project_body: dict[str, Any],
):
    response = await client.patch(
        f"/project/v1/{uuid4()}",
        json=update_project_body
    )
    assert response.status_code == HTTP_404_NOT_FOUND


async def test_delete_exists_project(
        created_project_id: UUID,
        client: AsyncClient,
        update_project_body: dict[str, Any],
):
    response = await client.delete(
        f"/project/v1/{created_project_id}",
    )
    assert response.status_code == HTTP_204_NO_CONTENT

    response = await client.get(
        f"/project/v1/{created_project_id}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND


async def test_delete_not_exists_project(
        created_project_id: UUID,
        client: AsyncClient,
        update_project_body: dict[str, Any],
):
    response = await client.delete(
        f"/project/v1/{uuid4()}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND


async def test_get_projects(
        created_project_id: UUID,
        client: AsyncClient,
        create_project_body: dict[str, Any]
):
    project_count = 10
    first_projects_pack = 7
    second_projects_pack_limit = 3

    body = deepcopy(create_project_body)
    for i in range(project_count):
        body["name"] = f"name #{i}"
        response = await client.post(
            "/project/v1",
            json=body
        )
        assert response.status_code == HTTP_201_CREATED

    response = await client.get(
        "/project/v1/",
        params={
            "limit": first_projects_pack,
        }
    )
    assert response.status_code == HTTP_200_OK
    assert len(response.json()["items"]) == first_projects_pack
    for i, item in enumerate(response.json()["items"]):
        assert item["name"] == f"name #{i}"

    response = await client.get(
        "/project/v1/",
        params={
            "show_after_datetime": response.json().get("last_seen_datetime"),
            "show_after_id": response.json().get("last_seen_id"),
        }
    )

    assert response.status_code == HTTP_200_OK
    for i, item in enumerate(response.json()["items"]):
        assert item["name"] == f"name #{i + first_projects_pack}"
    assert len(response.json()["items"]) == second_projects_pack_limit
