"""FastAPI dependencies, grouped by shared infrastructure and service domain."""

from app.core.dependencies.infrastructure import (
    get_anilist_api,
    get_app_state,
    get_jikan_api,
    get_omdb_api,
    get_redis,
    get_repositories,
    get_tmdb_api,
)
from app.core.dependencies.metadata import (
    get_anilist_service,
    get_jikan_service,
    get_omdb_service,
    get_tmdb_service,
)
from app.core.dependencies.media import (
    get_anilist_detail_service,
    get_external_payload_repository,
    get_external_payload_service,
    get_mal_detail_service,
    get_media_core_ensure_service,
    get_media_core_service,
    get_media_detail_service,
    get_media_service,
    get_omdb_detail_service,
    get_redis_service,
    get_sync_expiry_policy,
    get_tmdb_detail_service,
)

__all__ = [name for name in globals() if name.startswith("get_")]
