from bson import ObjectId
import pytest
from datetime import datetime, timedelta, timezone
from pydantic import ValidationError

from app.enums.user_media_entry_enums import (
    MediaExternalSource,
    MediaType,
    UserMediaEntryStatus,
)
from app.models.user_media_entry_models import (
    UserMediaEntryCreate,
    UserMediaEntryDB,
    UserMediaEntryInsert,
    UserMediaEntryPagination,
    UserMediaEntryUpdate,
    UserMediaEntry,
)


def test_user_media_entry_create_accepts_alias_fields():
    model = UserMediaEntryCreate(
        externalId=101,
        externalSource=MediaExternalSource.ANILIST,
        mediaType=MediaType.ANIME,
        repeatCount=2,
        isFavorite=True,
        inLibrary=True,
    ) # type: ignore

    assert model.external_id == 101
    assert model.external_source == MediaExternalSource.ANILIST
    assert model.media_type == MediaType.ANIME
    assert model.repeat_count == 2
    assert model.is_favorite is True
    assert model.in_library is True


def test_user_media_entry_create_rejects_negative_repeat_count():
    with pytest.raises(ValidationError, match="repeat_count must be non-negative"):
        UserMediaEntryCreate(
            externalId=101,
            externalSource=MediaExternalSource.ANILIST,
            mediaType=MediaType.ANIME,
            repeatCount=-1,
        ) # type: ignore


def test_user_media_entry_insert_sets_timestamps_when_missing():
    before = datetime.now(timezone.utc)

    model = UserMediaEntryInsert(
        externalId=202,
        externalSource=MediaExternalSource.TMDB,
        mediaType=MediaType.MOVIE,
        user_id="user_1",
    ) # type: ignore

    after = datetime.now(timezone.utc)

    assert model.created_at is not None
    assert model.updated_at is not None
    assert before <= model.created_at <= after
    assert before <= model.updated_at <= after


def test_user_media_entry_insert_keeps_explicit_timestamps():
    created = datetime(2024, 1, 1, tzinfo=timezone.utc)
    updated = datetime(2024, 1, 2, tzinfo=timezone.utc)

    model = UserMediaEntryInsert(
        externalId=303,
        externalSource=MediaExternalSource.IGDB,
        mediaType=MediaType.GAME,
        user_id="user_2",
        created_at=created,
        updated_at=updated,
    ) # type: ignore

    assert model.created_at == created
    assert model.updated_at == updated


def test_user_media_entry_db_coerces_id_to_string():
    now = datetime.now(timezone.utc)
    oid = ObjectId()

    model = UserMediaEntryDB(
        _id=oid,
        external_id=404,
        external_source=MediaExternalSource.ANILIST,
        media_type=MediaType.MANGA,
        user_id="user_3",
        created_at=now,
        updated_at=now,
    ) # type: ignore

    assert model.id == str(oid)
    assert isinstance(model.id, str)


def test_user_media_entry_update_rejects_negative_repeat_count():
    with pytest.raises(ValidationError, match="repeat_count must be non-negative"):
        UserMediaEntryUpdate(repeatCount=-3) # type: ignore


def test_user_media_entry_update_to_update_dict_raises_for_empty_payload():
    model = UserMediaEntryUpdate() # type: ignore

    with pytest.raises(ValueError, match="No fields provided for update"):
        model.to_update_dict()


def test_user_media_entry_update_to_update_dict_adds_updated_at_and_snake_case_keys():
    before = datetime.now(timezone.utc)

    model = UserMediaEntryUpdate(
        status=UserMediaEntryStatus.CURRENT,
        repeatCount=5,
        isFavorite=True,
        inLibrary=False,
    )
    update_dict = model.to_update_dict()

    after = datetime.now(timezone.utc)

    assert update_dict["status"] == UserMediaEntryStatus.CURRENT
    assert update_dict["repeat_count"] == 5
    assert update_dict["is_favorite"] is True
    assert update_dict["in_library"] is False
    assert before <= update_dict["updated_at"] <= after


def test_user_media_entry_from_db_maps_fields_correctly():
    now = datetime.now(timezone.utc)
    db_entry = UserMediaEntryDB(
        _id="entry_1",
        external_id=505,
        external_source=MediaExternalSource.ANILIST,
        media_type=MediaType.ANIME,
        user_id="user_9",
        title="Sample",
        coverImage="https://example.com/cover.jpg",
        isAdult=False,
        status=UserMediaEntryStatus.COMPLETED,
        repeatCount=1,
        isFavorite=True,
        inLibrary=True,
        created_at=now,
        updated_at=now,
    )

    result = UserMediaEntry.from_db(db_entry)

    assert result.id == "entry_1"
    assert result.external_id == 505
    assert result.external_source == MediaExternalSource.ANILIST
    assert result.media_type == MediaType.ANIME
    assert result.user_id == "user_9"
    assert result.cover_image == "https://example.com/cover.jpg"
    assert result.status == UserMediaEntryStatus.COMPLETED
    assert result.repeat_count == 1


def test_user_media_entry_pagination_accepts_alias_fields():
    now = datetime.now(timezone.utc)
    item = UserMediaEntry(
        id="entry_2",
        externalId=606,
        externalSource=MediaExternalSource.TMDB,
        mediaType=MediaType.TV,
        userId="user_10",
        createdAt=now,
        updatedAt=now,
    ) # type: ignore

    page = UserMediaEntryPagination(
        results=[item],
        page=1,
        perPage=20,
        hasNextPage=False,
        total=1,
    )

    assert page.page == 1
    assert page.per_page == 20
    assert page.has_next_page is False
    assert page.total == 1
    assert len(page.results) == 1


def test_user_media_entry_update_updated_at_is_timezone_aware():
    model = UserMediaEntryUpdate(status=UserMediaEntryStatus.PLANNING) # type: ignore

    result = model.to_update_dict()

    assert result["updated_at"].tzinfo is not None
    assert result["updated_at"].utcoffset() == timedelta(0)
