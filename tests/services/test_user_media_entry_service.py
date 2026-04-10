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
from app.models.review_models import ReviewCreate, ReviewDB, ReviewUpdate
from app.models.user_media_entry_models import (
    UserMediaEntryCreate,
    UserMediaEntryDB,
    UserMediaEntryUpdate,
)
from app.services.user_media_entry_service import UserMediaEntryService
from app.services.review_service import ReviewService


@pytest.fixture
def mock_repository():
    return MagicMock()


@pytest.fixture
def mock_review_service():
    return MagicMock(spec=ReviewService)


@pytest.fixture
def service(mock_repository, mock_review_service):
    return UserMediaEntryService(mock_repository, mock_review_service)


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


def create_review_db(**overrides):
    defaults = {
        "_id": "review-1",
        "user_media_entry_id": "entry-1",
        "user_id": "user-1",
        "review": "Excellent watch",
        "rating": 8,
        "review_progress": 10,
        "written_at": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    return ReviewDB(**defaults)


# --- Entry CRUD tests ---


@pytest.mark.asyncio
async def test_create_entry_creates_and_returns_entry(service, mock_repository):
    request = UserMediaEntryCreate(
        externalId=1234,
        externalSource=MediaExternalSource.ANILIST,
        mediaType=MediaType.ANIME,
        title="Erased",
        status=UserMediaEntryStatus.CURRENT,
    )  # type: ignore
    db_entry = create_user_media_entry_db(external_id=1234, title="Erased")
    mock_repository.create_entry = AsyncMock(return_value=db_entry)

    result = await service.create_entry(request, "user-1")

    assert result.id == "507f1f77bcf86cd799439011"
    assert result.external_id == 1234
    created_insert = mock_repository.create_entry.call_args.args[0]
    assert created_insert.user_id == "user-1"
    assert created_insert.external_id == 1234


@pytest.mark.asyncio
async def test_get_entry_by_id_returns_owned_entry(service, mock_repository):
    db_entry = create_user_media_entry_db(user_id="user-1")
    mock_repository.get_entry_by_id = AsyncMock(return_value=db_entry)

    result = await service.get_entry_by_id("entry-1", "user-1")

    assert result.id == "507f1f77bcf86cd799439011"
    mock_repository.get_entry_by_id.assert_awaited_once_with("entry-1", "user-1")


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
async def test_update_entry_returns_updated_entry(service, mock_repository):
    existing = create_user_media_entry_db(user_id="user-1")
    updated = create_user_media_entry_db(user_id="user-1", in_library=False)
    mock_repository.get_entry_by_id = AsyncMock(return_value=existing)
    mock_repository.update_entry = AsyncMock(return_value=updated)
    update_data = UserMediaEntryUpdate(inLibrary=False)  # type: ignore

    result = await service.update_entry("entry-1", update_data, "user-1")

    assert result is not None
    assert result.in_library is False
    mock_repository.update_entry.assert_awaited_once_with(
        "entry-1", "user-1", update_data
    )


@pytest.mark.asyncio
async def test_update_entry_raises_when_entry_missing_after_update(
    service, mock_repository
):
    existing = create_user_media_entry_db(user_id="user-1")
    mock_repository.get_entry_by_id = AsyncMock(return_value=existing)
    mock_repository.update_entry = AsyncMock(return_value=None)

    with pytest.raises(RuntimeError, match="missing after update"):
        await service.update_entry(
            "entry-1", UserMediaEntryUpdate(status=UserMediaEntryStatus.CURRENT), "user-1"  # type: ignore
        )


@pytest.mark.asyncio
async def test_delete_entry_deletes_reviews_then_entry(
    service, mock_repository, mock_review_service
):
    entry = create_user_media_entry_db(user_id="user-1")
    mock_repository.get_entry_by_id = AsyncMock(return_value=entry)
    mock_review_service.delete_reviews_for_user_media_entry = AsyncMock()
    mock_repository.delete_entry = AsyncMock(return_value=MagicMock(acknowledged=True))

    await service.delete_entry("entry-1", "user-1")

    mock_review_service.delete_reviews_for_user_media_entry.assert_awaited_once_with(
        "entry-1", "user-1"
    )
    mock_repository.delete_entry.assert_awaited_once_with("entry-1", "user-1")


@pytest.mark.asyncio
async def test_delete_entry_raises_when_delete_not_acknowledged(
    service, mock_repository, mock_review_service
):
    entry = create_user_media_entry_db(user_id="user-1")
    mock_repository.get_entry_by_id = AsyncMock(return_value=entry)
    mock_review_service.delete_reviews_for_user_media_entry = AsyncMock()
    mock_repository.delete_entry = AsyncMock(return_value=MagicMock(acknowledged=False))

    with pytest.raises(RuntimeError, match="Delete operation not acknowledged"):
        await service.delete_entry("entry-1", "user-1")


@pytest.mark.asyncio
async def test_count_entries_by_user_id_returns_count(service, mock_repository):
    mock_repository.count_entries_by_user_id = AsyncMock(return_value=9)

    count = await service.count_entries_by_user_id("user-1")

    assert count == 9
    mock_repository.count_entries_by_user_id.assert_awaited_once_with("user-1")


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


@pytest.mark.asyncio
async def test_get_entries_escapes_regex_title_search(service, mock_repository):
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
        title_search="a.b*",
        is_adult=None,
    )

    passed_filters = mock_repository.get_entries.call_args.kwargs["filters"]
    assert passed_filters["title"]["$regex"] == "a\\.b\\*"


# --- Review delegation tests ---


@pytest.mark.asyncio
async def test_create_review_delegates_to_review_service(service, mock_review_service):
    """Test that create_review delegates to review_service."""
    review_request = ReviewCreate(rating=8.5, review="Great!")  # type: ignore
    expected_review = MagicMock()
    mock_review_service.create_review = AsyncMock(return_value=expected_review)

    result = await service.create_review(review_request, "entry-1", "user-1")

    assert result == expected_review
    mock_review_service.create_review.assert_called_once_with(
        review_request, "entry-1", "user-1"
    )


@pytest.mark.asyncio
async def test_get_reviews_for_user_media_entry_delegates_to_review_service(
    service, mock_review_service
):
    """Test that get_reviews_for_user_media_entry delegates to review_service."""
    reviews = [MagicMock(), MagicMock()]
    mock_review_service.get_reviews_for_user_media_entry = AsyncMock(
        return_value=reviews
    )

    result = await service.get_reviews_for_user_media_entry("entry-1", "user-1")

    assert result == reviews
    mock_review_service.get_reviews_for_user_media_entry.assert_called_once_with(
        "entry-1", "user-1"
    )


@pytest.mark.asyncio
async def test_get_review_by_id_delegates_to_review_service(
    service, mock_review_service
):
    """Test that get_review_by_id delegates to review_service."""
    expected_review = MagicMock()
    mock_review_service.get_review_by_id = AsyncMock(return_value=expected_review)

    result = await service.get_review_by_id("review-1", "user-1", "entry-1")

    assert result == expected_review
    mock_review_service.get_review_by_id.assert_called_once_with(
        "review-1", "user-1", "entry-1"
    )


@pytest.mark.asyncio
async def test_count_reviews_for_user_media_entry_delegates_to_review_service(
    service, mock_review_service
):
    """Test that count_reviews_for_user_media_entry delegates to review_service."""
    mock_review_service.count_reviews_for_user_media_entry = AsyncMock(return_value=3)

    result = await service.count_reviews_for_user_media_entry("entry-1", "user-1")

    assert result == 3
    mock_review_service.count_reviews_for_user_media_entry.assert_called_once_with(
        "entry-1", "user-1"
    )


@pytest.mark.asyncio
async def test_update_review_delegates_to_review_service(service, mock_review_service):
    """Test that update_review delegates to review_service."""
    update_request = ReviewUpdate(rating=9.0)  # type: ignore
    expected_review = MagicMock()
    mock_review_service.update_review = AsyncMock(return_value=expected_review)

    result = await service.update_review(
        "review-1", "entry-1", update_request, "user-1"
    )

    assert result == expected_review
    mock_review_service.update_review.assert_called_once_with(
        "review-1", "entry-1", update_request, "user-1"
    )


@pytest.mark.asyncio
async def test_delete_review_delegates_to_review_service(service, mock_review_service):
    """Test that delete_review delegates to review_service."""
    mock_review_service.delete_review = AsyncMock()

    await service.delete_review("entry-1", "review-1", "user-1")

    mock_review_service.delete_review.assert_called_once_with(
        "entry-1", "review-1", "user-1"
    )


@pytest.mark.asyncio
async def test_delete_reviews_for_user_media_entry_delegates_to_review_service(
    service, mock_review_service
):
    """Test that delete_reviews_for_user_media_entry delegates to review_service."""
    mock_review_service.delete_reviews_for_user_media_entry = AsyncMock()

    await service.delete_reviews_for_user_media_entry("entry-1", "user-1")

    mock_review_service.delete_reviews_for_user_media_entry.assert_called_once_with(
        "entry-1", "user-1"
    )
