from typing import Optional

from app.models.db.external_storage_models import MovieWithCollection
from app.models.api.media_response_models import (
    AnimeDetailed,
    MangaDetailed,
    MovieDetailedWithCollection,
    TVDetailed,
)
from app.models.db.media_core_models import MediaDB
from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.mal_models import MALAnimeResponse, MALMangaResponse
from app.models.providers.omdb_models import OMDbData
from app.models.providers.tmdb_models import TMDBTVDetail
from app.utils.normalizers.anilist_normalizer import AnilistNormalizer
from app.utils.normalizers.score_builder import ScoreBuilder
from app.utils.normalizers.tmdb_normalizer import TMDBNormalizer


class MediaNormalizer:
    @staticmethod
    def to_movie_detailed_with_collection(
        media_core: MediaDB,
        data: MovieWithCollection,
        omdb_data: Optional[OMDbData] = None,
    ) -> MovieDetailedWithCollection:
        movie, collection = data.movie, data.collection
        collection = (
            TMDBNormalizer.get_movie_collection(collection) if collection else None
        )
        movie_detailed = TMDBNormalizer.normalize_movie_detailed(movie)

        scores = ScoreBuilder.build_movie_or_tv_score(movie, omdb_data)

        movie_detailed.scores = scores
        movie_detailed.id = str(media_core.id)  
        return MovieDetailedWithCollection(
            **movie_detailed.model_dump(),
            collection=collection,
        )

    @staticmethod
    def to_tv_detailed(
        media_core: MediaDB,
        tv: TMDBTVDetail, omdb_data: Optional[OMDbData] = None
    ) -> TVDetailed:
        tv_detailed = TMDBNormalizer.normalize_tv_detailed(tv)

        scores = ScoreBuilder.build_movie_or_tv_score(tv, omdb_data)
        tv_detailed.scores = scores
        tv_detailed.id = str(media_core.id)

        return tv_detailed

    @staticmethod
    def to_anime_detailed(
        media_core: MediaDB,
        anime: AnilistMediaDetail,
        mal_data: Optional[MALAnimeResponse] = None,
    ) -> AnimeDetailed:
        
        anime_detailed = AnilistNormalizer.normalize_anime_detailed(anime)
        scores = ScoreBuilder.build_anime_or_manga_score(anime, mal_data)

        anime_detailed.scores = scores
        anime_detailed.id = str(media_core.id)

        anime_detailed.background = (
            mal_data.data.background if mal_data and mal_data.data.background else None
        )
        return anime_detailed

    @staticmethod
    def to_manga_detailed(
        media_core: MediaDB,
        manga: AnilistMediaDetail, mal_data: Optional[MALMangaResponse] = None
    ) -> MangaDetailed:
        manga_detailed = AnilistNormalizer.normalize_manga_detailed(manga)
        scores = ScoreBuilder.build_anime_or_manga_score(manga, mal_data)

        manga_detailed.scores = scores
        manga_detailed.id = str(media_core.id)
        manga_detailed.background = (
            mal_data.data.background if mal_data and mal_data.data.background else None
        )
        manga_detailed.authors = (
            [author.name for author in mal_data.data.authors]
            if mal_data and mal_data.data.authors
            else None
        )

        return manga_detailed
