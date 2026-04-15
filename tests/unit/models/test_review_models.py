from datetime import datetime, timedelta, timezone

from bson import ObjectId
import pytest
from pydantic import ValidationError

from app.models.review_models import (
    Review,
    ReviewCreate,
    ReviewDB,
    ReviewInsert,
    ReviewUpdate,
)


def test_review_create_accepts_alias_fields():
    now = datetime.now(timezone.utc)

    model = ReviewCreate(
        review="Great",
        rating=8.5,
        reviewProgress=12,
        writtenAt=now,
    )

    assert model.review == "Great"
    assert model.rating == 8.5
    assert model.review_progress == 12
    assert model.written_at == now


def test_review_base_rejects_future_written_at():
    future = datetime.now(timezone.utc) + timedelta(days=1)

    with pytest.raises(
        ValidationError, match="Written at date cannot be in the future"
    ):
        ReviewCreate(
            writtenAt=future,
        )  # type: ignore


def test_review_update_to_update_dict_raises_for_empty_payload():
    model = ReviewUpdate()  # type: ignore

    with pytest.raises(ValueError, match="No fields provided for update"):
        model.to_update_dict()


def test_review_update_to_update_dict_adds_updated_at():
    before = datetime.now(timezone.utc)
    model = ReviewUpdate(rating=7.5, reviewProgress=20)  # type: ignore

    update_dict = model.to_update_dict()
    after = datetime.now(timezone.utc)

    assert update_dict["rating"] == 7.5
    assert update_dict["review_progress"] == 20
    assert before <= update_dict["updated_at"] <= after
    assert update_dict["updated_at"].tzinfo is not None


def test_review_insert_sets_timestamps_when_missing():
    before = datetime.now(timezone.utc)

    model = ReviewInsert(
        user_media_entry_id="entry_2",
        user_id="user_1",
    )  # type: ignore

    after = datetime.now(timezone.utc)

    assert model.created_at is not None
    assert model.updated_at is not None
    assert before <= model.created_at <= after
    assert before <= model.updated_at <= after


def test_review_db_coerces_object_id_to_string():
    now = datetime.now(timezone.utc)
    oid = ObjectId()

    model = ReviewDB(
        _id=oid,
        user_media_entry_id="entry_3",
        user_id="user_2",
        created_at=now,
        updated_at=now,
    )  # type: ignore

    assert model.id == str(oid)
    assert isinstance(model.id, str)


def test_review_from_db_maps_fields_to_api_model():
    now = datetime.now(timezone.utc)
    db_model = ReviewDB(
        _id="rev_1",
        user_media_entry_id="entry_9",
        user_id="user_9",
        review="Nice",
        rating=9.0,
        reviewProgress=24,
        writtenAt=now,
        created_at=now,
        updated_at=now,
    )

    api_model = Review.from_db(db_model)

    assert api_model.id == "rev_1"
    assert api_model.user_media_entry_id == "entry_9"
    assert api_model.user_id == "user_9"
    assert api_model.review == "Nice"
    assert api_model.rating == 9.0
    assert api_model.review_progress == 24
    assert api_model.written_at == now
    assert api_model.created_at == now
    assert api_model.updated_at == now


def test_review_response_model_accepts_alias_fields():
    now = datetime.now(timezone.utc)

    model = Review(
        id="rev_2",
        userMediaEntryId="entry_10",
        userId="user_10",
        createdAt=now,
        updatedAt=now,
        rating=8,
    )  # type: ignore

    assert model.user_media_entry_id == "entry_10"
    assert model.user_id == "user_10"
    assert model.created_at == now
    assert model.updated_at == now
    assert model.rating == 8


def test_review_base_accepts_all_optional_fields():
    """Test ReviewBase with all optional fields provided."""
    now = datetime.now(timezone.utc)
    model = ReviewCreate(
        review="Excellent series",
        rating=9.5,
        reviewProgress=20,
        writtenAt=now,
    )
    assert model.review == "Excellent series"
    assert model.rating == 9.5
    assert model.review_progress == 20
    assert model.written_at == now


def test_review_base_allows_partial_fields():
    """Test ReviewBase with only some fields."""
    model = ReviewCreate(rating=7.0) # type: ignore
    assert model.review is None
    assert model.rating == 7.0
    assert model.review_progress is None
    assert model.written_at is None


def test_review_base_rejects_negative_rating():
    """Test that negative ratings are rejected."""
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        ReviewCreate(rating=-1) # type: ignore


def test_review_base_rejects_out_of_range_rating():
    """Test that ratings over 10 are rejected."""
    with pytest.raises(ValidationError, match="less than or equal to 10"):
        ReviewCreate(rating=10.1) # type: ignore


def test_review_insert_preserves_all_fields():
    """Test ReviewInsert preserves all base fields."""
    now = datetime.now(timezone.utc)
    model = ReviewInsert(
        user_media_entry_id="entry_1",
        user_id="user_1",
        review="Fantastic!",
        rating=9.0,
        review_progress=15, # type: ignore
        written_at=now, # type: ignore
    )
    assert model.review == "Fantastic!"
    assert model.rating == 9.0
    assert model.review_progress == 15
    assert model.written_at == now


def test_review_db_round_trip():
    """Test that ReviewDB can be created and converted."""
    now = datetime.now(timezone.utc)
    original = ReviewDB(
        _id="rev_001",
        user_media_entry_id="entry_1",
        user_id="user_1",
        review="Great!",
        rating=8.5,
        review_progress=10, # type: ignore
        written_at=now, # type: ignore
        created_at=now,
        updated_at=now,
    )

    assert original.id == "rev_001"
    assert original.user_id == "user_1"
    assert original.user_media_entry_id == "entry_1"


def test_review_api_model_uses_aliases():
    """Test that Review API model uses proper aliases in JSON."""
    now = datetime.now(timezone.utc)
    api_model = Review(
        id="rev_1",
        userMediaEntryId="entry_1",
        userId="user_1",
        review="Good!",
        rating=7.0,
        createdAt=now,
        updatedAt=now,
    ) # type: ignore

    assert api_model.user_media_entry_id == "entry_1"
    assert api_model.user_id == "user_1"


def test_review_update_excludes_unset_fields():
    """Test that ReviewUpdate.to_update_dict excludes unset fields."""
    model = ReviewUpdate(rating=8.0) # type: ignore
    update_dict = model.to_update_dict()

    assert "rating" in update_dict
    assert "review" not in update_dict
    assert "review_progress" not in update_dict
    assert "written_at" not in update_dict
    assert "updated_at" in update_dict


def test_review_insert_custom_timestamps():
    """Test ReviewInsert with custom timestamps."""
    past = datetime(2024, 1, 1, tzinfo=timezone.utc)
    model = ReviewInsert(
        user_media_entry_id="entry_1",
        user_id="user_1",
        created_at=past,
        updated_at=past,
    ) # type: ignore

    assert model.created_at == past
    assert model.updated_at == past
