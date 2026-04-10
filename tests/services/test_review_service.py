import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from pymongo.results import DeleteResult

from app.core.exceptions import NotFoundException
from app.services.review_service import ReviewService
from app.repositories.review_repository import ReviewRepository
from app.models.review_models import (
    Review,
    ReviewCreate,
    ReviewDB,
    ReviewUpdate,
)


@pytest.fixture
def mock_review_repository():
    return MagicMock(spec=ReviewRepository)


@pytest.fixture
def review_service(mock_review_repository):
    return ReviewService(
        review_repository=mock_review_repository,
    )


def create_review_db(**overrides):
    """Create a mock ReviewDB object for testing."""
    defaults = {
        "_id": "review_123",
        "user_media_entry_id": "entry_456",
        "user_id": "user_789",
        "rating": 8.5,
        "review": "Great anime!",
        "review_progress": 12,
        "written_at": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    return ReviewDB(**defaults)


# --- Tests for create_review ---


@pytest.mark.asyncio
async def test_create_review_success(review_service, mock_review_repository):
    """Test successful review creation."""
    review = create_review_db()
    mock_review_repository.create_review = AsyncMock(return_value=review)

    review_request = ReviewCreate(review="Great anime!", rating=8.5) # type: ignore
    result = await review_service.create_review(review_request, "entry_456", "user_789")

    assert result.id == "review_123"
    assert result.review == "Great anime!"
    assert result.rating == 8.5
    mock_review_repository.create_review.assert_called_once()


@pytest.mark.asyncio
async def test_create_review_passes_correct_data(
    review_service, mock_review_repository
):
    """Test that create_review passes correct data to repository."""
    review = create_review_db()
    mock_review_repository.create_review = AsyncMock(return_value=review)

    review_request = ReviewCreate(review="Great!", rating=8.5) # type: ignore
    await review_service.create_review(review_request, "entry_456", "user_789")

    insert_data = mock_review_repository.create_review.call_args.args[0]
    assert insert_data.user_id == "user_789"
    assert insert_data.user_media_entry_id == "entry_456"
    assert insert_data.rating == 8.5
    assert insert_data.review == "Great!"


# --- Tests for update_review ---


@pytest.mark.asyncio
async def test_update_review_success(review_service, mock_review_repository):
    """Test successful review update."""
    updated_review = create_review_db(rating=9.0)
    mock_review_repository.update_review = AsyncMock(return_value=updated_review)

    update_request = ReviewUpdate(rating=9.0) # type: ignore
    result = await review_service.update_review(
        "review_123", "entry_456", update_request, "user_789"
    )

    assert result.rating == 9.0
    mock_review_repository.update_review.assert_called_once_with(
        "review_123", "entry_456", update_request, "user_789"
    )


@pytest.mark.asyncio
async def test_update_review_not_found(review_service, mock_review_repository):
    """Test update review raises RuntimeError when review not found after update."""
    mock_review_repository.update_review = AsyncMock(return_value=None)

    update_request = ReviewUpdate(rating=9.0) # type: ignore
    with pytest.raises(RuntimeError, match="Review missing after update"):
        await review_service.update_review(
            "review_123", "entry_456", update_request, "user_789"
        )


# --- Tests for delete_review ---


@pytest.mark.asyncio
async def test_delete_review_success(review_service, mock_review_repository):
    """Test successful review deletion."""
    delete_result = MagicMock(spec=DeleteResult)
    delete_result.acknowledged = True
    mock_review_repository.delete_review = AsyncMock(return_value=delete_result)

    await review_service.delete_review("entry_456", "review_123", "user_789")

    mock_review_repository.delete_review.assert_called_once_with(
        "review_123", "user_789", "entry_456"
    )


@pytest.mark.asyncio
async def test_delete_review_not_acknowledged(review_service, mock_review_repository):
    """Test delete review raises RuntimeError when not acknowledged."""
    delete_result = MagicMock(spec=DeleteResult)
    delete_result.acknowledged = False
    mock_review_repository.delete_review = AsyncMock(return_value=delete_result)

    with pytest.raises(RuntimeError, match="Failed to delete review"):
        await review_service.delete_review("entry_456", "review_123", "user_789")


# --- Tests for get_reviews_for_user_media_entry ---


@pytest.mark.asyncio
async def test_get_reviews_for_user_media_entry_success(
    review_service, mock_review_repository
):
    """Test retrieving reviews for a user media entry."""
    reviews = [create_review_db(), create_review_db(rating=7.0)]
    mock_review_repository.get_reviews_by_user_media_entry_id_and_user_id = AsyncMock(
        return_value=reviews
    )

    result = await review_service.get_reviews_for_user_media_entry(
        "entry_456", "user_789"
    )

    assert result is not None
    assert len(result) == 2
    assert result[0].id == "review_123"
    mock_review_repository.get_reviews_by_user_media_entry_id_and_user_id.assert_called_once_with(
        "entry_456", "user_789"
    )


@pytest.mark.asyncio
async def test_get_reviews_for_user_media_entry_empty(
    review_service, mock_review_repository
):
    """Test retrieving reviews when none exist returns None."""
    mock_review_repository.get_reviews_by_user_media_entry_id_and_user_id = AsyncMock(
        return_value=None
    )

    result = await review_service.get_reviews_for_user_media_entry(
        "entry_456", "user_789"
    )

    assert result is None


# --- Tests for get_review_by_id ---


@pytest.mark.asyncio
async def test_get_review_by_id_success(review_service, mock_review_repository):
    """Test retrieving a review by ID."""
    review = create_review_db()
    mock_review_repository.get_review_by_id = AsyncMock(return_value=review)

    result = await review_service.get_review_by_id(
        "review_123", "user_789", "entry_456"
    )

    assert result.id == "review_123"
    mock_review_repository.get_review_by_id.assert_called_once_with(
        "review_123", "user_789", "entry_456"
    )


@pytest.mark.asyncio
async def test_get_review_by_id_not_found(review_service, mock_review_repository):
    """Test get review raises NotFoundException when review not found."""
    mock_review_repository.get_review_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Review review_123 not found"):
        await review_service.get_review_by_id("review_123", "user_789", "entry_456")


@pytest.mark.asyncio
async def test_get_review_by_id_handles_repository_error(
    review_service, mock_review_repository
):
    """Test get review raises NotFoundException on any repository error."""
    mock_review_repository.get_review_by_id = AsyncMock(
        side_effect=Exception("DB error")
    )

    with pytest.raises(NotFoundException, match="Review review_123 not found"):
        await review_service.get_review_by_id("review_123", "user_789", "entry_456")


# --- Tests for count_reviews_for_user_media_entry ---


@pytest.mark.asyncio
async def test_count_reviews_for_user_media_entry(
    review_service, mock_review_repository
):
    """Test counting reviews for a media entry."""
    mock_review_repository.count_reviews_by_user_media_entry_id = AsyncMock(
        return_value=5
    )

    result = await review_service.count_reviews_for_user_media_entry(
        "entry_456", "user_789"
    )

    assert result == 5
    mock_review_repository.count_reviews_by_user_media_entry_id.assert_called_once_with(
        "entry_456", "user_789"
    )


# --- Tests for delete_reviews_for_user_media_entry ---


@pytest.mark.asyncio
async def test_delete_reviews_for_user_media_entry_success(
    review_service, mock_review_repository
):
    """Test deleting all reviews for a media entry."""
    delete_result = MagicMock(spec=DeleteResult)
    delete_result.acknowledged = True
    delete_result.deleted_count = 3
    mock_review_repository.delete_reviews_by_user_media_entry_id = AsyncMock(
        return_value=delete_result
    )

    await review_service.delete_reviews_for_user_media_entry("entry_456", "user_789")

    mock_review_repository.delete_reviews_by_user_media_entry_id.assert_called_once_with(
        "entry_456", "user_789"
    )


@pytest.mark.asyncio
async def test_delete_reviews_for_user_media_entry_not_acknowledged(
    review_service, mock_review_repository
):
    """Test delete raises RuntimeError when not acknowledged."""
    delete_result = MagicMock(spec=DeleteResult)
    delete_result.acknowledged = False
    mock_review_repository.delete_reviews_by_user_media_entry_id = AsyncMock(
        return_value=delete_result
    )

    with pytest.raises(RuntimeError, match="Failed to delete reviews"):
        await review_service.delete_reviews_for_user_media_entry(
            "entry_456", "user_789"
        )


# --- Tests for delete_all_reviews_for_user ---


@pytest.mark.asyncio
async def test_delete_all_reviews_for_user_success(
    review_service, mock_review_repository
):
    """Test deleting all reviews for a user."""
    delete_result = MagicMock(spec=DeleteResult)
    delete_result.acknowledged = True
    delete_result.deleted_count = 10
    mock_review_repository.delete_by_user_id = AsyncMock(return_value=delete_result)

    await review_service.delete_all_reviews_for_user("user_789")

    mock_review_repository.delete_by_user_id.assert_called_once_with("user_789")


@pytest.mark.asyncio
async def test_delete_all_reviews_for_user_not_acknowledged(
    review_service, mock_review_repository
):
    """Test delete all raises RuntimeError when not acknowledged."""
    delete_result = MagicMock(spec=DeleteResult)
    delete_result.acknowledged = False
    mock_review_repository.delete_by_user_id = AsyncMock(return_value=delete_result)

    with pytest.raises(RuntimeError, match="not acknowledged"):
        await review_service.delete_all_reviews_for_user("user_789")
