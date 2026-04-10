import pytest
from httpx import AsyncClient
from tests.integration.conftest import create_entry

pytestmark = pytest.mark.asyncio

async def test_create_entry(auth_client: AsyncClient):
    entry = await create_entry(auth_client)
    assert entry["title"] == "Test Movie"
    assert "id" in entry

async def test_get_entry_by_id(auth_client: AsyncClient):
    entry = await create_entry(auth_client)
    res = await auth_client.get(f"/user-media-entries/{entry['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == entry["id"]

async def test_get_entry_not_found(auth_client: AsyncClient):
    res = await auth_client.get("/user-media-entries/000000000000000000000000")
    assert res.status_code == 404

async def test_update_entry(auth_client: AsyncClient):
    entry = await create_entry(auth_client)
    res = await auth_client.patch(f"/user-media-entries/{entry['id']}", json={
        "in_library": True
    })
    assert res.status_code == 200
    assert res.json()["in_library"] is True

async def test_delete_entry(auth_client: AsyncClient):
    entry = await create_entry(auth_client)
    res = await auth_client.delete(f"/user-media-entries/{entry['id']}")
    assert res.status_code == 204

    get_res = await auth_client.get(f"/user-media-entries/{entry['id']}")
    assert get_res.status_code == 404

async def test_cannot_access_other_users_entry(
    auth_client: AsyncClient, second_auth_client: AsyncClient
):
    entry = await create_entry(auth_client)
    res = await second_auth_client.get(f"/user-media-entries/{entry['id']}")
    assert res.status_code == 403  # or 404 depending on your validator

async def test_get_entries_pagination(auth_client: AsyncClient):
    for i in range(5):
        await create_entry(auth_client, title=f"Movie {i}")
    res = await auth_client.get("/user-media-entries/?page=1&perPage=3")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 3