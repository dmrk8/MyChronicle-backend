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

    with pytest.raises(ValidationError, match="Written at date cannot be in the future"):
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