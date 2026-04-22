from typing import Optional

import structlog
from datetime import datetime, timedelta, timezone

from app.enums.media_enums import (
    DataFreshnessStatus,
    MediaExternalSource,
    MediaType,
    StoredDataType,
    SyncFrequency,
)
from app.models.api.anilist_models import AnilistMediaDetailed, CoverImage, MediaDate
from app.models.api.omdb_models import OMDbData
from app.models.api.tmdb_models import TMDBMovieDetail, TMDBTVDetail
from app.models.db.external__storage_models import MovieWithCollection
from app.services.anilist_service import AnilistService
from app.services.external_storage_service import ExternalStorageService
from app.services.media_db_service import MediaDatabaseService
from app.services.omdb_service import OMDbService
from app.services.tmdb_service import TMDBService
from app.utils.media_db_normalizer import MediaDBNormalizer

from app.utils.tmdb_normalizer import TMDBNormalizer

logger = structlog.get_logger().bind(service="SyncService")


class SyncService:
    def __init__(
        self,
        anilist_service: AnilistService,
        tmdb_service: TMDBService,
        external_storage_service: ExternalStorageService,
        media_database_service: MediaDatabaseService,
        omdb_service: OMDbService,
    ):
        self.anilist_service = anilist_service
        self.tmdb_service = tmdb_service
        self.external_storage_service = external_storage_service
        self.media_database_service = media_database_service
        self.omdb_service = omdb_service

    async def sync_anilist_media(self, external_id: int, media_type: MediaType):
        anilist_media = await self.anilist_service.get_media_detail(external_id)

        sync_frequency, expires_at = await self._calculate_anilist_sync_expiry(
            anilist_media
        )
        await self.external_storage_service.upsert(
            external_id=external_id,
            external_source=MediaExternalSource.ANILIST,
            media_type=media_type,
            sync_frequency=sync_frequency,
            payload=anilist_media.model_dump(),
            payload_type=StoredDataType.MEDIA_DETAILS,
            expires_at=expires_at,
        )
        await self.media_database_service.create_anilist_detail(anilist_media)

    async def sync_tmdb_movie(self, external_id: int, media_type: MediaType):
        tmdb_movie = await self.tmdb_service.get_movie_detail(external_id)
        sync_frequency, expires_at = await self._calculate_tmdb_movie_sync_expiry(
            tmdb_movie
        )
        omdb_data = None
        if tmdb_movie and tmdb_movie.imdb_id:
            omdb_data = await self._sync_omdb_data(
                imdb_id=tmdb_movie.imdb_id,
                external_id=external_id,
                media_type=media_type,
            )

        if tmdb_movie.belongs_to_collection:
            collection = await self.tmdb_service.get_collection_detail(
                tmdb_movie.belongs_to_collection.id
            )
            payload = MovieWithCollection(movie=tmdb_movie, collection=collection)
        else:
            payload = MovieWithCollection(movie=tmdb_movie, collection=None)

        await self.external_storage_service.upsert(
            external_id=external_id,
            external_source=MediaExternalSource.TMDB,
            media_type=media_type,
            sync_frequency=sync_frequency,
            payload=payload.model_dump(),
            payload_type=StoredDataType.MEDIA_DETAILS,
            expires_at=expires_at,
        )
        await self.media_database_service.create_tmdb_movie_detail(
            tmdb_movie, omdb_data
        )

    async def sync_tmdb_tv(self, external_id: int, media_type: MediaType):
        tmdb_tv = await self.tmdb_service.get_tv_detail(external_id)
        sync_frequency, expires_at = await self._calculate_tmdb_tv_sync_expiry(tmdb_tv)

        omdb_data = None
        if tmdb_tv.external_ids and tmdb_tv.external_ids.imdb_id:
            omdb_data = await self._sync_omdb_data(
                imdb_id=tmdb_tv.external_ids.imdb_id,
                external_id=external_id,
                media_type=media_type,
            )

        if tmdb_tv:
            await self.external_storage_service.upsert(
                external_id=external_id,
                external_source=MediaExternalSource.TMDB,
                media_type=media_type,
                sync_frequency=sync_frequency,
                payload=tmdb_tv.model_dump(),
                payload_type=StoredDataType.MEDIA_DETAILS,
                expires_at=expires_at,
            )
            await self.media_database_service.create_tmdb_tv_detail(tmdb_tv, omdb_data)

    async def _sync_omdb_data(
        self,
        imdb_id: str,
        external_id: int,
        media_type: MediaType,
    ):
        omdb_data = await self.external_storage_service.get_by_external_id_and_source_and_media_type(
            external_id=external_id,
            external_source=MediaExternalSource.OMDB,
            media_type=media_type,
        )
        if omdb_data:
            if omdb_data.freshness_status == DataFreshnessStatus.FRESH:
                return OMDbData.model_validate(omdb_data.payload)

        omdb_data = await self.omdb_service.fetch_data(imdb_id=imdb_id)

        if omdb_data:
            await self.external_storage_service.upsert(
                external_id=external_id,
                external_source=MediaExternalSource.OMDB,
                media_type=media_type,
                sync_frequency=SyncFrequency.MANUAL,
                payload=omdb_data.model_dump(),
                payload_type=StoredDataType.OMDB_DATA,
                expires_at=datetime.now(timezone.utc) + timedelta(days=180),
            )
            return omdb_data
        return None

    async def _calculate_anilist_sync_expiry(self, media: AnilistMediaDetailed):
        status = (media.status or "").upper()
        has_start_date = media.start_date is not None and (
            media.start_date.year or media.start_date.month or media.start_date.day
        )
        now = datetime.now(timezone.utc)

        if (
            status == "RELEASING"
            and media.next_airing_episode
            and media.next_airing_episode.airing_at
        ):
            airing_at = media.next_airing_episode.airing_at
            if airing_at:
                airing_at_dt = datetime.fromtimestamp(airing_at, tz=timezone.utc)
                return SyncFrequency.HIGH, airing_at_dt + timedelta(hours=1)
        elif (
            status == "NOT_YET_RELEASED"
            and has_start_date
            and media.start_date is not None
        ):
            year = media.start_date.year or now.year
            month = media.start_date.month or 1
            day = media.start_date.day or 1
            start_dt = datetime(year, month, day, tzinfo=timezone.utc)
            return SyncFrequency.MANUAL, start_dt
        return SyncFrequency.MANUAL, now + timedelta(days=30)

    async def _calculate_tmdb_movie_sync_expiry(self, media: TMDBMovieDetail):
        now = datetime.now(timezone.utc)
        if media.release_date:
            release_dt = datetime.strptime(media.release_date, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            if release_dt > now:
                return SyncFrequency.MANUAL, release_dt
        return SyncFrequency.MANUAL, now + timedelta(days=30)

    async def _calculate_tmdb_tv_sync_expiry(self, media: TMDBTVDetail):
        now = datetime.now(timezone.utc)
        status = (media.status or "").strip()

        air_date_str = (
            media.next_episode_to_air.air_date
            if media.next_episode_to_air and media.next_episode_to_air.air_date
            else None
        )
        if status == "Returning Series" and air_date_str:
            try:
                air_dt = datetime.strptime(air_date_str, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
                expires_at = air_dt + timedelta(hours=1)
                return SyncFrequency.HIGH, expires_at
            except Exception:
                return SyncFrequency.HIGH, now + timedelta(hours=1)
        return SyncFrequency.MANUAL, now + timedelta(days=30)

    async def _should_update_core_anilist(
        self, media: AnilistMediaDetailed, media_type: MediaType
    ) -> bool:
        old_media = (
            await self.media_database_service.get_media_by_external_id_and_source(
                media.id, MediaExternalSource.ANILIST, media_type
            )
        )
        if not old_media:
            return True

        if (
            old_media.status != media.status
            or old_media.release_date != self._to_datetime(media.start_date)
            or old_media.title.english != media.title.english
            or old_media.cover_image != self._get_best_cover_image(media.cover_image)
            or old_media.banner_image != media.banner_image
            or old_media.end_date != self._to_datetime(media.end_date)
        ):
            return True

        return False

    def _to_datetime(self, media_date: Optional[MediaDate]) -> Optional[datetime]:
        if not media_date or not media_date.year:
            return None
        return datetime(
            year=media_date.year,
            month=media_date.month or 1,
            day=media_date.day or 1,
        )

    def _get_best_cover_image(self, cover_image: Optional[CoverImage]) -> Optional[str]:
        if not cover_image:
            return None
        return cover_image.extra_large or cover_image.large or cover_image.medium

    async def _should_update_core_tmdb_movie(self, media: TMDBMovieDetail) -> bool:
        old_media = (
            await self.media_database_service.get_media_by_external_id_and_source(
                media.id, MediaExternalSource.TMDB, MediaType.MOVIE
            )
        )
        if not old_media:
            return True

        if (
            old_media.status != media.status
            or old_media.title != MediaDBNormalizer.build_tmdb_title(media)
            or old_media.release_date != media.release_date
            or old_media.title.title != media.title
            or old_media.title.title != media.original_title
            or old_media.cover_image
            != TMDBNormalizer.get_image_url(
                media.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
            )
            or old_media.banner_image
            != TMDBNormalizer.get_image_url(
                media.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
            )
        ):
            return True

        return False

    async def _should_update_core_tmdb_tv(self, media: TMDBTVDetail) -> bool:
        old_media = (
            await self.media_database_service.get_media_by_external_id_and_source(
                media.id, MediaExternalSource.TMDB, MediaType.TV
            )
        )
        if not old_media:
            return True

        if (
            old_media.status != media.status
            or old_media.release_date != media.first_air_date
            or old_media.title.title != media.name
            or old_media.title.title != media.original_name
            or old_media.cover_image
            != TMDBNormalizer.get_image_url(
                media.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
            )
            or old_media.banner_image
            != TMDBNormalizer.get_image_url(
                media.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
            )
        ):
            return True

        return False
