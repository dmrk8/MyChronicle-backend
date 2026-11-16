from datetime import datetime, timedelta, timezone

from app.enums.anilist_enums import AnilistStatus
from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.tmdb_models import TMDBTVDetail

from app.utils.time_helpers import utc_now

DEFAULT_TTL = timedelta(days=7)
PROVIDER_BUFFER = timedelta(minutes=10)


def _until_event(event_time: datetime | None) -> timedelta:
    if event_time is None:
        return DEFAULT_TTL

    return min(
        DEFAULT_TTL,
        max(event_time - utc_now(), timedelta(0)) + PROVIDER_BUFFER,
    )


class SyncExpiryPolicy:
    async def calculate_omdb_sync_ttl(self) -> timedelta:
        return timedelta(days=14)

    async def calculate_anilist_sync_ttl(self, media: AnilistMediaDetail) -> timedelta:
        if media.status == AnilistStatus.RELEASING:
            if media.next_airing_episode and media.next_airing_episode.airing_at:
                airing_at = datetime.fromtimestamp(
                    media.next_airing_episode.airing_at,
                    tz=timezone.utc,
                )
                return _until_event(airing_at)

        if media.status == AnilistStatus.NOT_YET_RELEASED and media.start_date:
            release_at = datetime(
                media.start_date.year or utc_now().year,
                media.start_date.month or 1,
                media.start_date.day or 1,
                tzinfo=timezone.utc,
            )
            return _until_event(release_at)

        return DEFAULT_TTL

    async def calculate_tmdb_movie_sync_ttl(self) -> timedelta:
        return timedelta(days=14)

    async def calculate_tmdb_tv_sync_ttl(self, media: TMDBTVDetail) -> timedelta:
        if media.next_episode_to_air and media.next_episode_to_air.air_date:
            air_date = datetime.strptime(
                media.next_episode_to_air.air_date,
                "%Y-%m-%d",
            ).replace(tzinfo=timezone.utc)

            return _until_event(air_date)

        return DEFAULT_TTL

    async def calculate_mal_sync_ttl(self) -> timedelta:
        return timedelta(days=7)
