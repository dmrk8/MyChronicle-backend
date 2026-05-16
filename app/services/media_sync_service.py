from typing import Optional, Union

import structlog
from datetime import datetime, timedelta, timezone


from app.enums.anilist_enums import AnilistStatus
from app.models.providers.mal_models import MALAnimeResponse, MALMangaResponse
from app.services.jikan_service import JikanService
from app.utils.normalizers.omdb_normalizer import OMDbNormalizer
from app.utils.time_helpers import utc_now

from app.enums.media_enums import (
    MediaExternalSource,
    MediaType,
    StoredDataType,
)
from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.omdb_models import OMDbData
from app.models.providers.tmdb_models import TMDBMovieDetail, TMDBTVDetail
from app.models.db.external_storage_models import MovieWithCollection
from app.services.anilist_service import AnilistService
from app.services.external_storage_service import ExternalStorageService
from app.services.media_core_service import MediaCoreService
from app.services.omdb_service import OMDbService
from app.services.tmdb_service import TMDBService

logger = structlog.get_logger()


class SyncService:
    def __init__(
        self,
        anilist_service: AnilistService,
        tmdb_service: TMDBService,
        external_storage_service: ExternalStorageService,
        media_core_service: MediaCoreService,
        omdb_service: OMDbService,
        jikan_service: JikanService,
    ):
        self.anilist_service = anilist_service
        self.tmdb_service = tmdb_service
        self.external_storage_service = external_storage_service
        self.media_core_service = media_core_service
        self.omdb_service = omdb_service
        self.jikan_service = jikan_service
        self.logger = logger.bind(service="SyncService")

    async def sync_anilist_media(self, external_id: int, media_type: MediaType):
        anilist_media = await self.anilist_service.get_media_detail(external_id)

        expires_at = await self._calculate_anilist_sync_expiry(anilist_media)

        mal_data = None
        if anilist_media.id_mal:
            mal_data = await self._get_or_sync_mal_data(
                mal_id=anilist_media.id_mal,
                media_type=media_type.value,
            )

        await self.external_storage_service.upsert(
            external_id=external_id,
            external_source=MediaExternalSource.ANILIST,
            media_type=media_type,
            payload=anilist_media,
            payload_type=StoredDataType.MEDIA_DETAILS,
            expires_at=expires_at,
        )

        existing = await self.media_core_service.get_media(
            primary_id=external_id,
            external_source=MediaExternalSource.ANILIST,
            media_type=media_type,
        
        )
        
        if not existing:
            if media_type == MediaType.ANIME and isinstance(mal_data, MALAnimeResponse):
                await self.media_core_service.create_anime_detail(
                    anilist_media, mal_data
                )
            elif media_type == MediaType.MANGA and isinstance(mal_data, MALMangaResponse):
                await self.media_core_service.create_manga_detail(
                    anilist_media, mal_data
                )

            
        
        self.logger.debug(
            "Synced Anilist media",
            external_id=external_id,
            media_type=media_type,
            source=MediaExternalSource.ANILIST,
        )

    async def sync_tmdb_movie(self, external_id: int, media_type: MediaType):
        tmdb_movie = await self.tmdb_service.get_movie_detail(external_id)
        expires_at = await self._calculate_tmdb_movie_sync_expiry(tmdb_movie)

        omdb_data = None
        if tmdb_movie and tmdb_movie.imdb_id:
            omdb_data = await self._get_or_sync_omdb_data(
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
            payload=payload,
            payload_type=StoredDataType.MEDIA_DETAILS,
            expires_at=expires_at,
        )

        existing = await self.media_core_service.get_media(
            primary_id=external_id,
            external_source=MediaExternalSource.TMDB,
            media_type=media_type,
        )
        if not existing:
            await self.media_core_service.create_movie_detail(
                tmdb_movie, omdb_data
            )

        self.logger.debug(
            "Synced TMDB movie",
            external_id=external_id,
            media_type=media_type,
            source=MediaExternalSource.TMDB,
        )

    async def sync_tmdb_tv(self, external_id: int, media_type: MediaType):
        tmdb_tv = await self.tmdb_service.get_tv_detail(external_id)
        expires_at = await self._calculate_tmdb_tv_sync_expiry(tmdb_tv)

        omdb_data = None
        if tmdb_tv.external_ids and tmdb_tv.external_ids.imdb_id:
            omdb_data = await self._get_or_sync_omdb_data(
                imdb_id=tmdb_tv.external_ids.imdb_id,
                external_id=external_id,
                media_type=media_type,
            )

        await self.external_storage_service.upsert(
            external_id=external_id,
            external_source=MediaExternalSource.TMDB,
            media_type=media_type,
            payload=tmdb_tv,
            payload_type=StoredDataType.MEDIA_DETAILS,
            expires_at=expires_at,
        )

        existing = await self.media_core_service.get_media(
            primary_id=external_id,
            external_source=MediaExternalSource.TMDB,
            media_type=media_type,
        )
        if not existing:
            await self.media_core_service.create_tv_detail(tmdb_tv, omdb_data)

        self.logger.debug(
            "Synced TMDB TV show",
            external_id=external_id,
            media_type=media_type,
            source=MediaExternalSource.TMDB,
        )

    async def _get_or_sync_omdb_data(
        self,
        imdb_id: str,
        external_id: int,
        media_type: MediaType,
    ) -> OMDbData:
        omdb_data = await self.external_storage_service.get_by_external_id_and_source_and_media_type(
            external_id=external_id,
            external_source=MediaExternalSource.OMDB,
            media_type=media_type,
        )

        if omdb_data and omdb_data.is_fresh:
            return OMDbData.model_validate(omdb_data.payload)

        omdb_data = await self.omdb_service.fetch_data(imdb_id=imdb_id)

        expires_at = await self._calculate_omdb_sync_expiry(omdb_data)

        # OMDb record are keyed by TMDB or Anilist ID, not OMDb ID,
        # imdb_id is stored in the payload for reference
        await self.external_storage_service.upsert(
            external_id=external_id,
            external_source=MediaExternalSource.OMDB,
            media_type=media_type,
            payload=omdb_data,
            payload_type=StoredDataType.OMDB_DATA,
            expires_at=expires_at,
        )
        
        return omdb_data
        
        

    async def _calculate_omdb_sync_expiry(
        self, omdb_data: OMDbData
    ) -> Optional[datetime]:
        now = utc_now()

        # Ongoing Series : "2019–"
        if (
            omdb_data.Type == "series"
            and omdb_data.Year
            and omdb_data.Year.endswith("–")
        ):
            return now + timedelta(days=180)

        # Ended Series: "2019–2023"
        if omdb_data.Type == "series" and omdb_data.Year and "–" in omdb_data.Year:
            end_year = OMDbNormalizer.parse_end_year(omdb_data.Year)
            if end_year and (now.year - end_year) < 2:
                return now + timedelta(days=365)
            return None  # ended long ago, unlikely to change (stable)

        # Movies or ended series - check release recency
        released = OMDbNormalizer.parse_released(omdb_data.Released)
        if released:
            age_days = (now - released).days
            if age_days < 180:
                return now + timedelta(days=90)  # Recent release, sync more frequently
            elif age_days < 365:
                return now + timedelta(
                    days=180
                )  # Moderately recent, sync every 6 months

        return None  # Older media, unlikely to change (stable)

    async def _calculate_anilist_sync_expiry(
        self, media: AnilistMediaDetail
    ) -> datetime:
        """
        Calculate Anilist media sync expiry based on media status
            and airing/release dates. For currently releasing media, sync more frequently
            (every 1 hour) to capture status and episode changes.
            For upcoming media, sync more frequently as the release date approaches.
            For completed or cancelled media, sync less frequently (every 30 days)
            since details are unlikely to change.

        Args:
            media (AnilistMediaDetail):

        Returns:
            _type_: datetime: The calculated expiry datetime for the Anilist media sync.
        """

        now = utc_now()

        status = (media.status or "").upper()

        if (
            status == AnilistStatus.RELEASING
            and media.next_airing_episode
            and media.next_airing_episode.airing_at
        ):
            airing_at = datetime.fromtimestamp(
                media.next_airing_episode.airing_at, tz=timezone.utc
            )
            return airing_at + timedelta(hours=1)

        if status == AnilistStatus.NOT_YET_RELEASED and media.start_date:
            try:
                year = media.start_date.year or now.year
                month = media.start_date.month or 1
                day = media.start_date.day or 1

                start_dt = datetime(year, month, day, tzinfo=timezone.utc)

                return max(start_dt, now) + timedelta(hours=3)
            except Exception:
                pass
        return now + timedelta(days=90)

    async def _calculate_tmdb_movie_sync_expiry(
        self, media: TMDBMovieDetail
    ) -> datetime:
        """Calculate tmdb expirery based on release date.
        For unreleased movies, sync more frequently as release date approaches.

        Args:
            media (TMDBMovieDetail):

        Returns:
            datetime: _description_
        """
        now = utc_now()
        if media.release_date:
            try:
                release_dt = datetime.strptime(media.release_date, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
                if release_dt > now:
                    return release_dt + timedelta(hours=1)

                if release_dt > now - timedelta(days=30):
                    return now + timedelta(days=30)
            except Exception:
                pass
        return now + timedelta(days=90)

    async def _calculate_tmdb_tv_sync_expiry(self, media: TMDBTVDetail) -> datetime:
        """Calculate tmdb expirery based on next episode air date or last air date.
            For currently airing shows, sync more frequently (every 1 hour) to capture status and episode changes.
            For upcoming shows, sync more frequently as the release date approaches.
            For completed shows, sync less frequently (every 90 days) since details are unlikely to change.

        Args:
            media (TMDBTVDetail):

        Returns:
            datetime: _description_
        """
        now = utc_now()

        air_date_str = (
            media.next_episode_to_air.air_date
            if media.next_episode_to_air and media.next_episode_to_air.air_date
            else None
        )
        if air_date_str:
            try:
                air_dt = datetime.strptime(air_date_str, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
                return max(air_dt, now) + timedelta(hours=1)
            except Exception:
                return now + timedelta(hours=1)

        if media.last_air_date:
            try:
                last_air_dt = datetime.strptime(
                    media.last_air_date, "%Y-%m-%d"
                ).replace(tzinfo=timezone.utc)
                if last_air_dt > now - timedelta(days=30):
                    return now + timedelta(days=30)
            except Exception:
                pass

        return now + timedelta(days=90)

    async def _calculate_mal_sync_expiry(
        self, mal_data: MALAnimeResponse | MALMangaResponse
    ) -> Optional[datetime]:
        if isinstance(mal_data, MALAnimeResponse):
            media = mal_data.data
            now = utc_now()
            if media.airing:
                return now + timedelta(weeks=1)
            else:
                return None
        if isinstance(mal_data, MALMangaResponse):
            media = mal_data.data
            now = utc_now()
            if media.publishing:
                return now + timedelta(days=60)
            else:
                return None

    async def _get_or_sync_mal_data(
        self, mal_id: int, media_type: str
    ) -> Union[MALAnimeResponse, MALMangaResponse]:
        mal_data = await self.external_storage_service.get_by_external_id_and_source_and_media_type(
            external_id=mal_id,
            external_source=MediaExternalSource.MAL,
            media_type=MediaType.ANIME if media_type == "ANIME" else MediaType.MANGA,
        )
        if mal_data and mal_data.is_fresh:
            if media_type == "ANIME":
                return MALAnimeResponse.model_validate(mal_data.payload)
            else:
                return MALMangaResponse.model_validate(mal_data.payload)

        mal_data = (
            await self.jikan_service.get_anime_details(mal_id)
            if media_type == "ANIME"
            else await self.jikan_service.get_manga_details(mal_id)
        )

        expires_at = await self._calculate_mal_sync_expiry(mal_data)

        await self.external_storage_service.upsert(
            external_id=mal_id,
            external_source=MediaExternalSource.MAL,
            media_type=MediaType.ANIME if media_type == "ANIME" else MediaType.MANGA,
            payload=mal_data,
            payload_type=StoredDataType.MAL_DATA,
            expires_at=expires_at,
        )
        
        return mal_data
