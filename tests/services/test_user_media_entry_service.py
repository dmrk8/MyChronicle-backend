import sys
import types
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import ForbiddenException, NotFoundException
from app.enums.user_media_entry_enums import (
    MediaExternalSource,
    MediaType,
    UserMediaEntrySortFields,
    UserMediaEntrySortOptions,
    UserMediaEntryStatus,
)
from app.models.user_media_entry_models import UserMediaEntryDB


from app.repositories.review_repository import ReviewRepository
from app.services.user_media_entry_service import UserMediaEntryService


@pytest.fixture
def mock_repository():
    return MagicMock()


@pytest.fixture
def mock_review_repository():
    return MagicMock(spec=ReviewRepository)


@pytest.fixture
def service(mock_repository, mock_review_repository):
    return UserMediaEntryService(mock_repository, mock_review_repository)


def create_user_media_entry_db(**overrides):
    defaults = {
        "_id": "507f1f77bcf86cd799439011",
        "external_id": 1001,
        "external_source": MediaExternalSource.ANILIST,
        "media_type": MediaType.ANIME,
        "user_id": "user-1",
        "title": "Steins;Gate",
        "status": UserMediaEntryStatus.CURRENT,
        "in_library": True,
        "is_favorite": False,
        "is_adult": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    return UserMediaEntryDB(**defaults)


@pytest.mark.asyncio
async def test_get_entry_by_external_id_and_source_returns_entry(
    service, mock_repository
):
    db_entry = create_user_media_entry_db()
    mock_repository.get_entry_by_external_id_and_external_source_and_user_id = (
        AsyncMock(return_value=db_entry)
    )

    result = await service.get_entry_by_external_id_and_source(
        external_id=1001,
        external_source=MediaExternalSource.ANILIST,
        user_id="user-1",
    )

    assert result is not None
    assert result.id == "507f1f77bcf86cd799439011"
    mock_repository.get_entry_by_external_id_and_external_source_and_user_id.assert_awaited_once_with(
        1001,
        MediaExternalSource.ANILIST,
        "user-1",
    )


@pytest.mark.asyncio
async def test_get_entry_by_external_id_and_source_returns_none_when_missing(
    service, mock_repository
):
    mock_repository.get_entry_by_external_id_and_external_source_and_user_id = (
        AsyncMock(return_value=None)
    )

    result = await service.get_entry_by_external_id_and_source(
        external_id=1001,
        external_source=MediaExternalSource.ANILIST,
        user_id="user-1",
    )

    assert result is None


@pytest.mark.asyncio
async def test_delete_entry_deletes_reviews_then_entry(
    service, mock_repository, mock_review_repository
):
    entry = create_user_media_entry_db(user_id="user-1")
    mock_repository.get_entry_by_id = AsyncMock(return_value=entry)
    mock_review_repository.delete_reviews_by_user_media_entry_id = AsyncMock()
    mock_repository.delete_entry = AsyncMock(return_value=MagicMock(acknowledged=True))

    await service.delete_entry("entry-1", "user-1")

    mock_review_repository.delete_reviews_by_user_media_entry_id.assert_awaited_once_with(
        "entry-1", "user-1"
    )
    mock_repository.delete_entry.assert_awaited_once_with("entry-1", "user-1")


@pytest.mark.asyncio
async def test_delete_entry_raises_when_delete_not_acknowledged(
    service, mock_repository, mock_review_repository
):
    entry = create_user_media_entry_db(user_id="user-1")
    mock_repository.get_entry_by_id = AsyncMock(return_value=entry)
    mock_review_repository.delete_reviews_by_user_media_entry_id = AsyncMock()
    mock_repository.delete_entry = AsyncMock(return_value=MagicMock(acknowledged=False))

    with pytest.raises(RuntimeError, match="Delete operation not acknowledged"):
        await service.delete_entry("entry-1", "user-1")
        
@pytest.mark.asyncio
async def test_verify_ownership_raises_not_found(service, mock_repository):
    mock_repository.get_entry_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Entry entry-1 not found"):
        await service._verify_ownership("entry-1", "user-1")

@pytest.mark.asyncio
async def test_verify_ownership_raises_forbidden(service, mock_repository):
    entry = create_user_media_entry_db(user_id="other-user")
    mock_repository.get_entry_by_id = AsyncMock(return_value=entry)

    with pytest.raises(ForbiddenException, match="do not have access"):
        await service._verify_ownership("entry-1", "user-1")
        
@pytest.mark.asyncio
async def test_get_entries_uses_repo_count_with_user_scope(service, mock_repository):
    db_entry = create_user_media_entry_db()
    mock_repository.get_entries = AsyncMock(return_value=[db_entry])
    mock_repository.count_entries = AsyncMock(return_value=6)

    result = await service.get_entries(
        user_id="user-1",
        in_library=True,
        is_favorite=False,
        status="CURRENT",
        media_type="ANIME",
        page=1,
        per_page=5,
        sort_by=UserMediaEntrySortFields.CREATED_AT,
        sort_order=UserMediaEntrySortOptions.CREATED_AT_DESC,
        title_search="gate",
        is_adult=False,
    )

    assert result.total == 6
    assert result.has_next_page is True
    assert len(result.results) == 1

    expected_filters = {
        "in_library": True,
        "is_favorite": False,
        "status": "CURRENT",
        "media_type": "ANIME",
        "title": {"$regex": "gate", "$options": "i"},
        "$or": [
            {"is_adult": False},
            {"is_adult": {"$exists": False}},
            {"is_adult": None},
        ],
    }

    mock_repository.get_entries.assert_awaited_once_with(
        user_id="user-1",
        filters=expected_filters,
        page=1,
        per_page=5,
        sort_by=UserMediaEntrySortFields.CREATED_AT,
        sort_order=UserMediaEntrySortOptions.CREATED_AT_DESC,
    )
    mock_repository.count_entries.assert_awaited_once_with(
        user_id="user-1",
        filters=expected_filters,
    )


@pytest.mark.asyncio
async def test_get_entries_uses_is_adult_true_filter(service, mock_repository):
    mock_repository.get_entries = AsyncMock(return_value=[])
    mock_repository.count_entries = AsyncMock(return_value=0)

    await service.get_entries(
        user_id="user-1",
        in_library=None,
        is_favorite=None,
        status=None,
        media_type=None,
        page=1,
        per_page=20,
        sort_by=UserMediaEntrySortFields.UPDATED_AT,
        sort_order=UserMediaEntrySortOptions.UPDATED_AT_DESC,
        title_search=None,
        is_adult=True,
    )

    expected_filters = {"is_adult": True}
    mock_repository.get_entries.assert_awaited_once_with(
        user_id="user-1",
        filters=expected_filters,
        page=1,
        per_page=20,
        sort_by=UserMediaEntrySortFields.UPDATED_AT,
        sort_order=UserMediaEntrySortOptions.UPDATED_AT_DESC,
    )
    mock_repository.count_entries.assert_awaited_once_with(
        user_id="user-1",
        filters=expected_filters,
    )
