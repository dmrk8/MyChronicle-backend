from datetime import datetime, timezone

from bson import ObjectId
from pydantic import ValidationError
import pytest

from app.models.user_models import (
    User,
    UserDB,
    UserInsert,
    UserRole,
    UserUpdate,
    UpdatePassword,
)


def test_user_insert_accepts_valid_input():
    model = UserInsert(username="newuser", hash_password="hashed_pwd")

    assert model.username == "newuser"
    assert model.hash_password == "hashed_pwd"


@pytest.mark.parametrize(
    "password, expected_error",
    [
        ("PASSUPPER1@", "at least one lowercase letter"),
        ("passlower1@", "at least one uppercase letter"),
        ("passNoDigits@", "at least one digit"),
        ("passNoSymbol1", "at least one symbol"),
    ],
)
def test_update_password_rejects_weak_password(password, expected_error):
    with pytest.raises(ValidationError, match=expected_error):
        UpdatePassword(currentPassword="Current@Pass1", newPassword=password)


def test_user_insert_sets_timestamps_when_missing():
    before = datetime.now(timezone.utc)

    model = UserInsert(
        username="insert_user",
        hash_password="hashed_pwd",
    )

    after = datetime.now(timezone.utc)

    assert model.role == UserRole.USER
    assert model.created_at is not None
    assert model.updated_at is not None
    assert before <= model.created_at <= after
    assert before <= model.updated_at <= after


def test_user_insert_keeps_explicit_timestamps():
    created = datetime(2024, 1, 1, tzinfo=timezone.utc)
    updated = datetime(2024, 1, 2, tzinfo=timezone.utc)

    model = UserInsert(
        username="insert_user",
        hash_password="hashed_pwd",
        role=UserRole.ADMIN,
        created_at=created,
        updated_at=updated,
    )

    assert model.role == UserRole.ADMIN
    assert model.created_at == created
    assert model.updated_at == updated


def test_user_db_coerces_object_id_to_string():
    now = datetime.now(timezone.utc)
    oid = ObjectId()

    model = UserDB(
        _id=oid,  # type: ignore
        username="db_user",
        role=UserRole.USER,
        hash_password="hashed_pwd",
        created_at=now,
        updated_at=now,
    )

    assert model.id == str(oid)
    assert isinstance(model.id, str)


def test_user_update_to_update_dict_raises_for_empty_payload():
    model = UserUpdate()  # type: ignore

    with pytest.raises(ValueError, match="No fields provided for update"):
        model.to_update_dict()


def test_user_update_to_update_dict_adds_updated_at():
    before = datetime.now(timezone.utc)

    model = UserUpdate(username="renamed", hash_password="new_hash")
    update_dict = model.to_update_dict()

    after = datetime.now(timezone.utc)

    assert update_dict["username"] == "renamed"
    assert update_dict["hash_password"] == "new_hash"
    assert before <= update_dict["updated_at"] <= after


def test_user_from_db_maps_fields_to_api_model():
    now = datetime.now(timezone.utc)
    db_model = UserDB(
        _id="user_1",
        username="mapped_user",
        role=UserRole.USER,
        hash_password="hashed_pwd",
        created_at=now,
        updated_at=now,
    )

    api_model = User.from_db(db_model)

    assert api_model.id == "user_1"
    assert api_model.username == "mapped_user"
    assert api_model.role == UserRole.USER
    assert api_model.created_at == now
    assert api_model.updated_at == now


def test_user_response_model_accepts_alias_fields():
    now = datetime.now(timezone.utc)

    model = User(
        id="user_2",
        username="alias_user",
        role=UserRole.ADMIN,
        createdAt=now,
        updatedAt=now,
    )

    assert model.created_at == now
    assert model.updated_at == now
    assert model.role == UserRole.ADMIN
