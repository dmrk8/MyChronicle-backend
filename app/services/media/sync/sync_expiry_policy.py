from datetime import datetime, timedelta, timezone

from app.enums.anilist_enums import AnilistStatus
from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.mal_models import MALAnimeResponse, MALMangaResponse
from app.models.providers.omdb_models import OMDbData
from app.models.providers.tmdb_models import TMDBMovieDetail, TMDBTVDetail
from app.utils.normalizers.omdb_normalizer import OMDbNormalizer
from app.utils.time_helpers import utc_now


class SyncExpiryPolicy:
    async def calculate_omdb_sync_ttl(
        self,
        omdb_data: OMDbData,
    ) -> timedelta:
        now = utc_now()

        # Ongoing Series : "2019–"
        if (
            omdb_data.Type == "series"
            and omdb_data.Year
            and omdb_data.Year.endswith("–")
        ):
            return timedelta(days=180)

        # Ended Series: "2019–2023"
        if omdb_data.Type == "series" and omdb_data.Year and "–" in omdb_data.Year:
            end_year = OMDbNormalizer.parse_end_year(omdb_data.Year)
            if end_year and (now.year - end_year) < 2:
                return timedelta(days=365)

        # Movies or ended series - check release recency
        released = OMDbNormalizer.parse_released(omdb_data.Released)
        if released:
            age_days = (now - released).days
            if age_days < 180:
                return timedelta(days=90)  # Recent release, sync more frequently
            elif age_days < 365:
                return timedelta(days=180)  # Moderately recent, sync every 6 months

        return timedelta(days=365)  # Older releases, sync annually

    async def calculate_anilist_sync_ttl(
        self, media: AnilistMediaDetail
    ) -> timedelta:
        """
        Calculate Anilist media sync expiry based on media status

        For currently airing media -> sync after next episode airs (1 hour after airing)
        For upcoming media -> sync after release date (3 hours after release)

        For rest of the media -> sync every 90 days since details are unlikely to change.

        Args:
            media (AnilistMediaDetail):

        Returns:
            _type_: timedelta: The calculated expiry timedelta for the Anilist media sync.
        """

        now = utc_now()
        status = (media.status or "").upper()

        if (
            status == AnilistStatus.RELEASING
            and media.next_airing_episode
            and media.next_airing_episode.airing_at
        ):
            airing_at = datetime.fromtimestamp(
                media.next_airing_episode.airing_at,
                tz=timezone.utc,
            )
            return max(airing_at - now, timedelta(0)) + timedelta(hours=1)

        if status == AnilistStatus.NOT_YET_RELEASED and media.start_date:
            try:
                start_dt = datetime(
                    media.start_date.year or now.year,
                    media.start_date.month or 1,
                    media.start_date.day or 1,
                    tzinfo=timezone.utc,
                )
                return max(start_dt - now, timedelta(0)) + timedelta(hours=3)
            except ValueError:
                pass

        return timedelta(days=90)

    async def calculate_tmdb_movie_sync_ttl(
        self, media: TMDBMovieDetail
    ) -> timedelta:
        """Calculate tmdb expirery based on release date.
        if movie is upcoming: sync after release date (1 hour after release)
        if movie is recently released: sync after 30 days (to capture any changes)
        if movie is old: sync after 90 days (since details are unlikely to change)

        Args:
            media (TMDBMovieDetail):

        Returns:
            timedelta: _description_
        """
        now = utc_now()

        if media.release_date:
            try:
                release_dt = datetime.strptime(
                    media.release_date,
                    "%Y-%m-%d",
                ).replace(tzinfo=timezone.utc)

                if release_dt > now:
                    return release_dt - now + timedelta(hours=1)

                if release_dt > now - timedelta(days=30):
                    return timedelta(days=30)
            except ValueError:
                pass

        return timedelta(days=90)

    async def calculate_tmdb_tv_sync_ttl(self, media: TMDBTVDetail) -> timedelta:
        """Calculate tmdb expirery based on next episode air date or last air date.
            If next episode is upcoming: sync after next episode air date (1 hour after airing)
            If last episode aired within 30 days: sync after 30 days (to capture any changes)
            If last episode aired more than 30 days ago: sync after 90 days (since details are unlikely to change)

        Args:
            media (TMDBTVDetail):

        Returns:
            timedelta: _description_
        """
        now = utc_now()

        air_date = (
            media.next_episode_to_air.air_date
            if media.next_episode_to_air and media.next_episode_to_air.air_date
            else None
        )

        if air_date:
            try:
                air_dt = datetime.strptime(
                    air_date,
                    "%Y-%m-%d",
                ).replace(tzinfo=timezone.utc)

                return max(air_dt - now, timedelta(0)) + timedelta(hours=1)
            except ValueError:
                return timedelta(hours=1)

        if media.last_air_date:
            try:
                last_air_dt = datetime.strptime(
                    media.last_air_date,
                    "%Y-%m-%d",
                ).replace(tzinfo=timezone.utc)

                if last_air_dt > now - timedelta(days=30):
                    return timedelta(days=30)
            except ValueError:
                pass

        return timedelta(days=90)

    async def calculate_mal_sync_ttl(
        self, mal_data: MALAnimeResponse | MALMangaResponse
    ) -> timedelta:
        """
        Calculate the sync expiry for MAL data.
        if airing/publishing: sync after 1 week for anime and 60 days for manga
        if not airing/publishing: return None

        Args:
            mal_data (MALAnimeResponse | MALMangaResponse):

        Returns:
            Optional[timedelta]: _description_
        """
        if isinstance(mal_data, MALAnimeResponse):
            if mal_data.data.airing:
                return timedelta(weeks=1)

        if isinstance(mal_data, MALMangaResponse):
            if mal_data.data.publishing:
                return timedelta(days=60)

        return timedelta(days=360) 
