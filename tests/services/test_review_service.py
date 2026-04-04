import pytest
from unittest.mock import ANY, MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone
from pydantic import ValidationError

from app.core.exceptions import NotFoundException, ForbiddenException
from app.services.review_service import ReviewService
from app.repositories.review_repository import ReviewRepository
from app.core.event_bus import EventBus
from app.models.review_models import ReviewCreate, ReviewUpdate, ReviewDB


@pytest.fixture
def mock_review_repository():
    return MagicMock(spec=ReviewRepository)


@pytest.fixture
def mock_event_bus():
    bus = MagicMock(spec=EventBus)
    bus.publish = AsyncMock()
    return bus


@pytest.fixture
def review_service(mock_review_repository, mock_event_bus):
    return ReviewService(
        review_repository=mock_review_repository,
        event_bus=mock_event_bus,
    )


def create_review_db(**overrides):
    defaults = {
        "id": "review_123",
        "userMediaEntryId": "entry_456",
        "userId": "user_789",
        "rating": 8,
        "review": "Great anime!",
        "reviewProgress": 12,
        "writtenAt": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    return ReviewDB(**defaults)


# --- Model validation tests (no service needed) ---

def test_create_review_validates_rating_upper_bound():
    with pytest.raises(ValidationError, match="less than or equal to 10"):
        ReviewCreate(userMediaEntryId="entry_456", rating=11) # type: ignore


def test_create_review_validates_rating_lower_bound():
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        ReviewCreate(userMediaEntryId="entry_456", rating=-1) # type: ignore


def test_create_review_validates_review_length():
    with pytest.raises(ValidationError, match="at most 5000 characters"):
        ReviewCreate(userMediaEntryId="entry_456", review="x" * 5001) # type: ignore


def test_update_review_validates_rating():
    with pytest.raises(ValidationError, match="less than or equal to 10"):
        ReviewUpdate(rating=11) # type: ignore


def test_update_review_validates_written_at_future():
    with pytest.raises(ValidationError, match="cannot be in the future"):
        ReviewUpdate(writtenAt=datetime(2099, 1, 1, tzinfo=timezone.utc)) # type: ignore


# --- Service tests ---

@pytest.mark.asyncio
async def test_create_review_success(review_service, mock_review_repository, mock_event_bus):
    review_request = ReviewCreate(userMediaEntryId="entry_456", rating=8, review="Great anime!") # type: ignore

    mock_review_repository.create_review = AsyncMock(
        return_value=MagicMock(inserted_id="review_123")
    )

    result = await review_service.create_review(review_request, user_id="user_789")

    assert result.id == "review_123"
    assert result.user_media_entry_id == "entry_456"
    mock_review_repository.create_review.assert_called_once()
    mock_event_bus.publish.assert_called_once_with(
        "review.changed",
        review_id="review_123",
        user_media_entry_id="entry_456",
        occurred_at=result.created_at,
    )


@pytest.mark.asyncio
async def test_update_review_not_found(review_service, mock_review_repository):
    mock_review_repository.get_review_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Review .* not found"):
        await review_service.update_review(
            "nonexistent_id", ReviewUpdate(rating=9), user_id="user_789" # type: ignore
        )


@pytest.mark.asyncio
async def test_update_review_forbidden(review_service, mock_review_repository):
    existing_review = create_review_db(userId="other_user")
    mock_review_repository.get_review_by_id = AsyncMock(return_value=existing_review)

    with pytest.raises(ForbiddenException):
        await review_service.update_review(
            "review_123", ReviewUpdate(rating=9), user_id="user_789" # type: ignore
        )


@pytest.mark.asyncio
async def test_update_review_success(review_service, mock_review_repository, mock_event_bus):
    existing_review = create_review_db(rating=7)
    updated_review = create_review_db(rating=9)

    mock_review_repository.get_review_by_id = AsyncMock(
        side_effect=[existing_review, updated_review]
    )
    mock_review_repository.update_review = AsyncMock()

    result = await review_service.update_review(
        "review_123", ReviewUpdate(rating=9), user_id="user_789" # type: ignore
    )

    assert result.rating == 9
    mock_review_repository.update_review.assert_called_once()
    mock_event_bus.publish.assert_called_once()


@pytest.mark.asyncio
async def test_delete_review_not_found(review_service, mock_review_repository):
    mock_review_repository.get_review_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Review .* not found"):
        await review_service.delete_review("nonexistent_id", user_id="user_789")


@pytest.mark.asyncio
async def test_delete_review_forbidden(review_service, mock_review_repository):
    existing_review = create_review_db(userId="other_user")
    mock_review_repository.get_review_by_id = AsyncMock(return_value=existing_review)

    with pytest.raises(ForbiddenException):
        await review_service.delete_review("review_123", user_id="user_789")


@pytest.mark.asyncio
async def test_delete_review_success(review_service, mock_review_repository, mock_event_bus):
    existing_review = create_review_db()
    mock_review_repository.get_review_by_id = AsyncMock(return_value=existing_review)
    mock_review_repository.delete_review = AsyncMock(
        return_value=MagicMock(acknowledged=True)
    )

    result = await review_service.delete_review("review_123", user_id="user_789")

    assert result is True
    mock_review_repository.delete_review.assert_called_once_with("review_123")
    mock_event_bus.publish.assert_called_once_with(
        "review.deleted",
        review_id="review_123",
        user_id="user_789",
        occurred_at=ANY,
    )
    
    called_occurred_at = mock_event_bus.publish.call_args.kwargs["occurred_at"]
    assert isinstance(called_occurred_at, datetime)
    assert abs(datetime.now(timezone.utc) - called_occurred_at) < timedelta(seconds=1)


@pytest.mark.asyncio
async def test_get_review_by_id_not_found(review_service, mock_review_repository):
    mock_review_repository.get_review_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Review .* not found"):
        await review_service.get_review_by_id("nonexistent_id")


@pytest.mark.asyncio
async def test_get_review_by_id_success(review_service, mock_review_repository):
    review = create_review_db()
    mock_review_repository.get_review_by_id = AsyncMock(return_value=review)

    result = await review_service.get_review_by_id("review_123")

    assert result.id == "review_123"
    mock_review_repository.get_review_by_id.assert_called_once_with("review_123")


@pytest.mark.asyncio
async def test_get_reviews_for_user_media_entry_empty(review_service, mock_review_repository):
    mock_review_repository.get_reviews_by_user_media_entry_id = AsyncMock(return_value=None)

    result = await review_service.get_reviews_for_user_media_entry("entry_456")

    assert result == []


@pytest.mark.asyncio
async def test_get_reviews_for_user_media_entry_success(review_service, mock_review_repository):
    reviews = [create_review_db(), create_review_db(id="review_124")]
    mock_review_repository.get_reviews_by_user_media_entry_id = AsyncMock(return_value=reviews)

    result = await review_service.get_reviews_for_user_media_entry("entry_456")

    assert len(result) == 2
    mock_review_repository.get_reviews_by_user_media_entry_id.assert_called_once_with("entry_456")