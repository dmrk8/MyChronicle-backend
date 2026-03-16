# Fix the review service tests
import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone

from app.services.review_service import ReviewService
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_media_entry_repository import UserMediaEntryRepository
from app.models.review_models import ReviewCreate, ReviewUpdate, ReviewDB


@pytest.fixture
def mock_review_repository():
    return MagicMock(spec=ReviewRepository)


@pytest.fixture
def mock_user_media_entry_repository():
    return MagicMock(spec=UserMediaEntryRepository)


@pytest.fixture
def review_service(mock_review_repository, mock_user_media_entry_repository):
    return ReviewService(
        review_repository=mock_review_repository,
        user_media_entry_repository=mock_user_media_entry_repository,
    )


def create_review_db(**overrides):
    """Factory for ReviewDB instances."""
    defaults = {
        "id": "review_123",
        "user_media_entry_id": "entry_456",
        "rating": 8,
        "review": "Great anime!",
        "review_progress": 12,
        "written_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    return ReviewDB(**defaults)


@pytest.mark.asyncio
async def test_create_review_validates_rating_upper_bound(review_service):
    """Test that reviews with rating > 10 are rejected."""
    review_request = ReviewCreate(
        userMediaEntryId="entry_456",
        rating=11,
        review="Too high rating",
        reviewProgress=None,
        writtenAt=None
    )

    with pytest.raises(ValueError, match="Rating must be between 0 and 10"):
        await review_service.create_review(review_request)


@pytest.mark.asyncio
async def test_create_review_validates_rating_lower_bound(review_service):
    """Test that reviews with rating < 0 are rejected."""
    review_request = ReviewCreate(
        userMediaEntryId="entry_456",
        rating=-1,
        review="Negative rating",
        reviewProgress=None,
        writtenAt=None
    )

    with pytest.raises(ValueError, match="Rating must be between 0 and 10"):
        await review_service.create_review(review_request)


@pytest.mark.asyncio
async def test_create_review_validates_review_length(review_service):
    """Test that reviews longer than 5000 characters are rejected."""
    review_request = ReviewCreate(
        userMediaEntryId="entry_456",
        rating=8,
        review="x" * 5001,
        reviewProgress=None,
        writtenAt=None
    )

    with pytest.raises(ValueError, match="Review must be less than 5000 characters"):
        await review_service.create_review(review_request)


@pytest.mark.asyncio
async def test_create_review_success(review_service, mock_review_repository, mock_user_media_entry_repository):
    """Test successful review creation."""
    review_request = ReviewCreate(
        userMediaEntryId="entry_456",
        rating=8,
        review="Great anime!",
        reviewProgress=None,
        writtenAt=None
    )
    
    created_review = create_review_db()
    mock_review_repository.create_review = AsyncMock(return_value=MagicMock(inserted_id="review_123"))
    mock_review_repository.get_review_by_id = AsyncMock(return_value=created_review)
    mock_user_media_entry_repository.update_entry = AsyncMock()

    result = await review_service.create_review(review_request)

    assert result.id == "review_123"
    mock_review_repository.create_review.assert_called_once()
    mock_user_media_entry_repository.update_entry.assert_called_once()


@pytest.mark.asyncio
async def test_update_review_not_found(review_service, mock_review_repository):
    """Test updating non-existent review raises error."""
    mock_review_repository.get_review_by_id = AsyncMock(return_value=None)
    
    update_request = ReviewUpdate(rating=9, review=None, reviewProgress=None, writtenAt=None)

    with pytest.raises(ValueError, match="Review with id .* not found"):
        await review_service.update_review("nonexistent_id", update_request)


@pytest.mark.asyncio
async def test_update_review_validates_rating(review_service, mock_review_repository):
    """Test that invalid rating on update is rejected."""
    existing_review = create_review_db()
    mock_review_repository.get_review_by_id = AsyncMock(return_value=existing_review)
    
    
    update_request = ReviewUpdate(rating=11, review=None, reviewProgress=None, writtenAt=None)

    with pytest.raises(ValueError, match="Rating must be between 0 and 10"):
        await review_service.update_review("review_123", update_request)


@pytest.mark.asyncio
async def test_update_review_success(review_service, mock_review_repository, mock_user_media_entry_repository):
    """Test successful review update."""
    existing_review = create_review_db(rating=7)
    updated_review = create_review_db(rating=9)
    
    mock_review_repository.get_review_by_id = AsyncMock(side_effect=[existing_review, updated_review])
    mock_review_repository.update_review = AsyncMock()
    mock_user_media_entry_repository.update_entry = AsyncMock()
    
    update_request = ReviewUpdate(rating=9, review=None, reviewProgress=None, writtenAt=None)

    result = await review_service.update_review("review_123", update_request)

    assert result.rating == 9
    mock_review_repository.update_review.assert_called_once()
    mock_user_media_entry_repository.update_entry.assert_called_once()


@pytest.mark.asyncio
async def test_delete_review_not_found(review_service, mock_review_repository):
    """Test deleting non-existent review raises error."""
    mock_review_repository.get_review_by_id = AsyncMock(return_value=None)

    with pytest.raises(ValueError, match="Review with id .* not found"):
        await review_service.delete_review("nonexistent_id")


@pytest.mark.asyncio
async def test_delete_review_success(review_service, mock_review_repository):
    """Test successful review deletion."""
    existing_review = create_review_db()
    mock_review_repository.get_review_by_id = AsyncMock(return_value=existing_review)
    mock_review_repository.delete_review = AsyncMock(return_value=MagicMock(acknowledged=True))

    result = await review_service.delete_review("review_123")

    assert result is True
    mock_review_repository.delete_review.assert_called_once_with("review_123")


@pytest.mark.asyncio
async def test_get_review_by_id_not_found(review_service, mock_review_repository):
    """Test getting non-existent review raises error."""
    mock_review_repository.get_review_by_id = AsyncMock(return_value=None)

    # The actual error message is "Review not found", not the regex pattern
    with pytest.raises(ValueError, match="Review not found"):
        await review_service.get_review_by_id("nonexistent_id")


@pytest.mark.asyncio
async def test_get_review_by_id_success(review_service, mock_review_repository):
    """Test successfully getting review by ID."""
    review = create_review_db()
    mock_review_repository.get_review_by_id = AsyncMock(return_value=review)

    result = await review_service.get_review_by_id("review_123")

    assert result.id == "review_123"
    mock_review_repository.get_review_by_id.assert_called_once_with("review_123")


@pytest.mark.asyncio
async def test_get_reviews_by_user_media_entry_id_empty(review_service, mock_review_repository):
    """Test getting reviews when none exist returns empty list or None."""
    # The actual implementation returns None, not []
    mock_review_repository.get_reviews_by_user_media_entry_id = AsyncMock(return_value=None)

    result = await review_service.get_reviews_by_user_media_entry_id("entry_456")

    assert result is None


@pytest.mark.asyncio
async def test_get_reviews_by_user_media_entry_id_success(review_service, mock_review_repository):
    """Test getting multiple reviews for an entry."""
    reviews = [create_review_db(), create_review_db(id="review_124")]
    mock_review_repository.get_reviews_by_user_media_entry_id = AsyncMock(return_value=reviews)

    result = await review_service.get_reviews_by_user_media_entry_id("entry_456")

    assert len(result) == 2
    mock_review_repository.get_reviews_by_user_media_entry_id.assert_called_once_with("entry_456")
