from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from starlette.status import HTTP_201_CREATED, HTTP_409_CONFLICT, HTTP_200_OK, \
    HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

from tests.utils import compare_dict_fields


@pytest.fixture(scope="session")
def create_event_body() -> dict[str, Any]:
    return {
        "name": "event",
        "description": "string",
        "start_date": "2026-10-11T10:52:34.540Z",
        "end_date": "2026-10-11T10:52:34.540Z",
        "event_info": {
            "organizer": "string",
            "head_url": "https://example.com/",
            "location": "string"
        }
    }


@pytest.fixture(scope="session")
def update_event_body() -> dict[str, Any]:
    return {
        "name": "updated string",
        "description": "updated descr",
    }


@pytest.fixture(scope="session", autouse=True)
async def created_event_id(client: TestClient,
                           create_event_body: dict[str, Any]) -> str:
    response = client.post(
        "/event/v1",
        json=create_event_body
    )

    assert response.status_code == HTTP_201_CREATED
    event_id = response.json().get("id")
    assert event_id is not None and isinstance(event_id, str) and isinstance(
        UUID(event_id), UUID)
    return event_id


async def test_create_event_with_exists_name(
        client: TestClient,
        create_event_body: dict[str, Any],
):
    response = client.post(
        "/event/v1",
        json=create_event_body
    )

    assert response.status_code == HTTP_409_CONFLICT


async def test_get_exists_event(
        created_event_id: UUID,
        client: TestClient,
        create_event_body: dict[str, Any]
):
    response = client.get(
        f"/event/v1/{created_event_id}",
    )

    assert response.status_code == HTTP_200_OK
    compare_dict_fields(
        response.json(), create_event_body,
        only_include={"name", "description"}
    )
    compare_dict_fields(
        response.json()["event_info"], create_event_body["event_info"]
    )


async def test_get_not_exists_event(
        client: TestClient,
):
    response = client.get(
        f"/event/v1/{uuid4()}",
    )

    assert response.status_code == HTTP_404_NOT_FOUND


async def test_update_event_with_exists_name(
        created_event_id: UUID,
        client: TestClient,
        update_event_body: dict[str, Any],
):
    response = client.patch(
        f"/event/v1/{created_event_id}",
        json=update_event_body
    )
    assert response.status_code == HTTP_200_OK

    response = client.get(
        f"/event/v1/{created_event_id}",
    )
    assert response.status_code == HTTP_200_OK
    compare_dict_fields(
        response.json(), update_event_body,
        only_include={"name", "description"}
    )


async def test_delete_event(
        created_event_id: UUID,
        client: TestClient,
        update_event_body: dict[str, Any],
):
    response = client.delete(
        f"/event/v1/{created_event_id}",
    )
    assert response.status_code == HTTP_204_NO_CONTENT

    response = client.get(
        f"/event/v1/{created_event_id}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND


# TODO проверки
async def test_get_events(
        created_event_id: UUID,
        client: TestClient,
        create_event_body: dict[str, Any]
):
    event_count = 10
    first_events_pack = 7
    second_events_pack_limit = 3

    for i in range(event_count):
        create_event_body["name"] = f"name #{i}"
        client.post(
            "/event/v1",
            json=create_event_body
        )


    response = client.get(
        f"/event/v1/",
        params={
            "limit": first_events_pack,
        }
    )
    assert response.status_code == HTTP_200_OK
    assert len(response.json()["items"]) == first_events_pack
    for i, item in enumerate(response.json()["items"]):
        assert item["name"] == f"name #{i}"
    from src.logger import logger
    logger.info(response.json())

    response = client.get(
        f"/event/v1/",
        params={
            "show_after_datetime": response.json().get("last_seen_datetime"),
            "show_after_id" : response.json().get("last_seen_id"),
        }
    )

    for i, item in enumerate(response.json()["items"]):
        assert item["name"] == f"name #{i+first_events_pack}"

    assert response.status_code == HTTP_200_OK
    assert len(response.json()["items"]) == second_events_pack_limit
