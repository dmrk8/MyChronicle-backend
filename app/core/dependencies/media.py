from fastapi import Depends

from app.core.dependencies.metadata import (
    get_anilist_service,
    get_jikan_service,
    get_omdb_service,
    get_tmdb_service,
)
from app.core.dependencies.infrastructure import get_redis, get_repositories
from app.repositories.media.external_payload_repository import ExternalPayloadRepository
from app.repositories.registry import Repositories
from app.services.media.core.media_core_ensure_service import MediaCoreEnsureService
from app.services.media.core.media_core_service import MediaCoreService
from app.services.media.details.media_detail_service import MediaDetailService
from app.services.media.details.providers.anilist_detail_service import AnilistDetailService
from app.services.media.details.providers.mal_detail_service import MALDetailService
from app.services.media.details.providers.omdb_detail_service import OMDbDetailService
from app.services.media.details.providers.tmdb_detail_service import TMDBDetailService
from app.services.media.media_service import MediaService
from app.services.media.storage.external_payload_service import ExternalPayloadService
from app.services.media.sync.sync_expiry_policy import SyncExpiryPolicy
from app.services.metadata.anilist_service import AnilistService
from app.services.metadata.jikan_service import JikanService
from app.services.metadata.omdb_service import OMDbService
from app.services.metadata.tmdb_service import TMDBService
from app.services.redis_service import RedisService
from redis.asyncio import Redis


def get_redis_service(redis_client: Redis = Depends(get_redis)) -> RedisService:
    return RedisService(redis_client=redis_client)


def get_external_payload_repository(
    repositories: Repositories = Depends(get_repositories),
) -> ExternalPayloadRepository:
    return repositories.external_payload


def get_external_payload_service(
    repository: ExternalPayloadRepository = Depends(get_external_payload_repository),
) -> ExternalPayloadService:
    return ExternalPayloadService(repository=repository)


def get_media_core_service(
    repositories: Repositories = Depends(get_repositories),
) -> MediaCoreService:
    return MediaCoreService(repository=repositories.media_core)


def get_media_core_ensure_service(
    service: MediaCoreService = Depends(get_media_core_service),
) -> MediaCoreEnsureService:
    return MediaCoreEnsureService(service=service)


def get_sync_expiry_policy() -> SyncExpiryPolicy:
    return SyncExpiryPolicy()


def get_anilist_detail_service(
    anilist_service: AnilistService = Depends(get_anilist_service),
    external_payload_service: ExternalPayloadService = Depends(get_external_payload_service),
    sync_expiry_policy: SyncExpiryPolicy = Depends(get_sync_expiry_policy),
) -> AnilistDetailService:
    return AnilistDetailService(anilist_service, external_payload_service, sync_expiry_policy)


def get_mal_detail_service(
    jikan_service: JikanService = Depends(get_jikan_service),
    external_payload_service: ExternalPayloadService = Depends(get_external_payload_service),
    sync_expiry_policy: SyncExpiryPolicy = Depends(get_sync_expiry_policy),
) -> MALDetailService:
    return MALDetailService(jikan_service, external_payload_service, sync_expiry_policy)


def get_omdb_detail_service(
    omdb_service: OMDbService = Depends(get_omdb_service),
    external_payload_service: ExternalPayloadService = Depends(get_external_payload_service),
    sync_expiry_policy: SyncExpiryPolicy = Depends(get_sync_expiry_policy),
) -> OMDbDetailService:
    return OMDbDetailService(omdb_service, external_payload_service, sync_expiry_policy)


def get_tmdb_detail_service(
    tmdb_service: TMDBService = Depends(get_tmdb_service),
    external_payload_service: ExternalPayloadService = Depends(get_external_payload_service),
    sync_expiry_policy: SyncExpiryPolicy = Depends(get_sync_expiry_policy),
) -> TMDBDetailService:
    return TMDBDetailService(tmdb_service, external_payload_service, sync_expiry_policy)


def get_media_detail_service(
    anilist_detail_service: AnilistDetailService = Depends(get_anilist_detail_service),
    tmdb_detail_service: TMDBDetailService = Depends(get_tmdb_detail_service),
    mal_detail_service: MALDetailService = Depends(get_mal_detail_service),
    omdb_detail_service: OMDbDetailService = Depends(get_omdb_detail_service),
    media_core_ensure_service: MediaCoreEnsureService = Depends(get_media_core_ensure_service),
    tmdb_service: TMDBService = Depends(get_tmdb_service),
) -> MediaDetailService:
    return MediaDetailService(
        anilist_detail_service=anilist_detail_service,
        tmdb_detail_service=tmdb_detail_service,
        mal_detail_service=mal_detail_service,
        omdb_detail_service=omdb_detail_service,
        media_core_ensure_service=media_core_ensure_service,
        tmdb_service=tmdb_service,
    )


def get_media_service(
    redis_service: RedisService = Depends(get_redis_service),
    anilist_service: AnilistService = Depends(get_anilist_service),
    tmdb_service: TMDBService = Depends(get_tmdb_service),
    media_detail_service: MediaDetailService = Depends(get_media_detail_service),
) -> MediaService:
    return MediaService(
        redis_service=redis_service,
        anilist_service=anilist_service,
        tmdb_service=tmdb_service,
        media_detail_service=media_detail_service,
    )
