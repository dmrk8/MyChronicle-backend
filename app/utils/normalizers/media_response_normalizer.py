from typing import Optional

from app.models.db.external_storage_models import MovieWithCollection
from app.models.api.media_response import (
    AnimeDetailed,
    MangaDetailed,
    MovieDetailedWithCollection,
    TVDetailed,
)
from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.omdb_models import OMDbData
from app.models.providers.tmdb_models import TMDBTVDetail
from app.utils.normalizers.anilist_normalizer import AnilistNormalizer
from app.utils.normalizers.score_builder import ScoreBuilder
from app.utils.normalizers.tmdb_normalizer import TMDBNormalizer


class MediaNormalizer:
    @staticmethod
    def to_movie_detailed_with_collection(
        data: MovieWithCollection, omdb_data: Optional[OMDbData] = None
    ) -> MovieDetailedWithCollection:
        movie, collection = data.movie, data.collection
        collection = (
            TMDBNormalizer.get_movie_collection(collection) if collection else None
        )
        movie_detailed = TMDBNormalizer.normalize_movie_detailed(movie)

        scores = ScoreBuilder.build_tmdb_score(movie, omdb_data)

        movie_detailed.scores = scores
        return MovieDetailedWithCollection(
            **movie_detailed.model_dump(),
            collection=collection,
        )

    @staticmethod
    def to_tv_detailed(
        tv: TMDBTVDetail, omdb_data: Optional[OMDbData] = None
    ) -> TVDetailed:
        tv_detailed = TMDBNormalizer.normalize_tv_detailed(tv)

        scores = ScoreBuilder.build_tmdb_score(tv, omdb_data)
        tv_detailed.scores = scores

        return tv_detailed

    @staticmethod
    def to_anime_detailed(anime: AnilistMediaDetail) -> AnimeDetailed:
        anime_detailed = AnilistNormalizer.normalize_anime_detailed(anime)
        scores = ScoreBuilder.build_anilist_score(anime)

        anime_detailed.scores = scores
        return anime_detailed

    @staticmethod
    def to_manga_detailed(manga: AnilistMediaDetail) -> MangaDetailed:
        manga_detailed = AnilistNormalizer.normalize_manga_detailed(manga)
        scores = ScoreBuilder.build_anilist_score(manga)

        manga_detailed.scores = scores
        return manga_detailed
