from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.auth.auth_dependencies import get_current_user
from app.core.dependencies import get_user_service
from app.main import app

def setup_app_state_for_tests(app):
    app.state.settings = MagicMock()
    app.state.mongo_client = MagicMock()
    app.state.redis_client = MagicMock()
    app.state.anilist_client = MagicMock()
    app.state.tmdb_client = MagicMock()
    app.state.omdb_client = MagicMock()
    app.state.event_bus = MagicMock()
    app.state.password_handler = MagicMock()
    app.state.jwt_handler = MagicMock()
    app.state.repositories = MagicMock()


client = TestClient(app)


def test_change_username_unauthenticated():
    setup_app_state_for_tests(app)
    response = client.patch("/users/username", json={"username": "newname"})
    assert response.status_code == 401


def test_change_username_authenticated():
    setup_app_state_for_tests(app)

    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = lambda: MagicMock(id="user123")
    app.dependency_overrides[get_user_service] = lambda: MagicMock(
        update_username=AsyncMock(return_value=None)
    )
    response = client.patch("/users/username", json={"username": "newname"})
    assert response.status_code == 204
    app.dependency_overrides.clear()


def test_change_password_unauthenticated():
    setup_app_state_for_tests(app)
    response = client.patch(
        "/users/password", json={"current_password": "old", "new_password": "new"}
    )
    assert response.status_code == 401


def test_change_password_authenticated():
    setup_app_state_for_tests(app)

    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = lambda: MagicMock(id="user123")
    app.dependency_overrides[get_user_service] = lambda: MagicMock(
        change_password=AsyncMock(return_value=None)
    )
    response = client.patch(
        "/users/password",
        json={"current_password": "old", "new_password": "NewPass123!"},
    )
    assert response.status_code == 204
    app.dependency_overrides.clear()


def test_delete_user_unauthenticated():
    setup_app_state_for_tests(app)

    app.dependency_overrides.clear()

    response = client.delete("/users/")
    assert response.status_code == 401


def test_delete_user_authenticated():
    setup_app_state_for_tests(app)

    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = lambda: MagicMock(id="user123")
    app.dependency_overrides[get_user_service] = lambda: MagicMock(
        delete_user=AsyncMock(return_value=None)
    )
    response = client.delete("/users/")
    assert response.status_code == 204
    app.dependency_overrides.clear()
