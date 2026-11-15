from app.enums.media_enums import MediaType
from app.models.api.media_response_models import (
    AnimeDetail,
    MangaDetail,
    MovieDetail,
    TVDetail,
)
from app.services.media.details.providers.anilist_detail_service import (
    AnilistDetailService,
)
from app.services.media.details.providers.mal_detail_service import MALDetailService
from app.services.media.core.media_core_ensure_service import MediaCoreEnsureService
from app.services.media.details.media_response_assembler import MediaResponseAssembler
from app.services.media.details.providers.omdb_detail_service import OMDbDetailService
from app.services.media.details.providers.tmdb_collection_service import (
    TMDBCollectionService,
)
from app.services.media.details.providers.tmdb_detail_service import TMDBDetailService
from app.services.metadata.tmdb_service import TMDBService
from app.utils.normalizers.tmdb_normalizer import TMDBNormalizer


class MediaDetailService:
    """Fetch provider details, ensure the internal media record, and assemble API data."""

    def __init__(
        self,
        anilist_detail_service: AnilistDetailService,
        tmdb_detail_service: TMDBDetailService,
        mal_detail_service: MALDetailService,
        omdb_detail_service: OMDbDetailService,
        media_core_ensure_service: MediaCoreEnsureService,
        tmdb_service: TMDBService,
        tmdb_collection_service: TMDBCollectionService,
    ):
        self.anilist_detail_service = anilist_detail_service
        self.tmdb_detail_service = tmdb_detail_service
        self.mal_detail_service = mal_detail_service
        self.omdb_detail_service = omdb_detail_service
        self.media_core_ensure_service = media_core_ensure_service
        self.tmdb_service = tmdb_service
        self.tmdb_collection_service = tmdb_collection_service

    async def get_anime_detail(self, media_id: int) -> AnimeDetail:
        anilist = await self.anilist_detail_service.get_media_detail(media_id)
        mal = None
        if anilist.id_mal:
            mal = await self.mal_detail_service.get_anime_detail(anilist.id_mal)
        core = await self.media_core_ensure_service.ensure_anilist(anilist, mal)
        return MediaResponseAssembler.to_anime_detail(core, anilist, mal)

    async def get_manga_detail(self, media_id: int) -> MangaDetail:
        anilist = await self.anilist_detail_service.get_media_detail(media_id)
        mal = None
        if anilist.id_mal:
            mal = await self.mal_detail_service.get_manga_detail(anilist.id_mal)
        core = await self.media_core_ensure_service.ensure_anilist(anilist, mal)
        return MediaResponseAssembler.to_manga_detail(core, anilist, mal)

    async def get_movie_detail(self, media_id: int) -> MovieDetail:
        movie = await self.tmdb_detail_service.get_movie_detail(media_id)
        omdb = None
        if movie.imdb_id:
            omdb = await self.omdb_detail_service.get_data(movie.imdb_id)
        core = await self.media_core_ensure_service.ensure_tmdb_movie(movie, omdb)
        collection = None
        if movie.belongs_to_collection:
            raw_collection = await self.tmdb_collection_service.get_collection_detail(
                movie.belongs_to_collection.id
            )
            collection = TMDBNormalizer.get_movie_collection(raw_collection)
        return MediaResponseAssembler.to_movie_detail(core, movie, collection, omdb)

    async def get_tv_detail(self, media_id: int) -> TVDetail:
        tv = await self.tmdb_detail_service.get_tv_detail(media_id)
        omdb = None
        if tv.external_ids and tv.external_ids.imdb_id:
            omdb = await self.omdb_detail_service.get_data(tv.external_ids.imdb_id)
        core = await self.media_core_ensure_service.ensure_tmdb_tv(tv, omdb)
        return MediaResponseAssembler.to_tv_detail(core, tv, omdb)

    async def get_detail(
        self, media_id: int, media_type: MediaType
    ) -> AnimeDetail | MangaDetail | MovieDetail | TVDetail:
        """Dispatch to the provider appropriate for the unified media type."""
        if media_type == MediaType.ANIME:
            return await self.get_anime_detail(media_id)
        if media_type == MediaType.MANGA:
            return await self.get_manga_detail(media_id)
        if media_type == MediaType.MOVIE:
            return await self.get_movie_detail(media_id)
        if media_type == MediaType.TV:
            return await self.get_tv_detail(media_id)
        raise ValueError(f"Unsupported media type: {media_type}")
