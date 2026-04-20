from typing import Optional

from app.enums.media_enums import MediaExternalSource
from app.models.api.anilist_models import AnilistMediaDetailed
from app.models.api.omdb_models import OMDbData
from app.models.api.tmdb_models import TMDBTVDetail
from app.models.db.external__storage_models import MovieWithCollection
from app.models.db.media_db_models import MediaScore
from app.models.media_models import (
    AnimeDetailed,
    MangaDetailed,
    MovieDetailedWithCollection,
    TVDetailed,
)
from app.utils.anilist_normalizer import AnilistNormalizer
from app.utils.omdb_normalizer import normalize_omdb_rating
from app.utils.tmdb_normalizer import TMDBNormalizer


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

        scores = normalize_omdb_rating(omdb_data) if omdb_data else []
        if movie.vote_average is not None:
            scores.append(
                MediaScore(
                    source=MediaExternalSource.TMDB.value,
                    value=movie.vote_average,
                    vote_count=movie.vote_count,
                )
            )
        movie_detailed.media_scores = scores
        return MovieDetailedWithCollection(
            movie=movie_detailed,
            collection=collection,
        )

    @staticmethod
    def to_tv_detailed(
        tv: TMDBTVDetail, omdb_data: Optional[OMDbData] = None
    ) -> TVDetailed:
        tv_detailed = TMDBNormalizer.normalize_tv_detailed(tv)
        scores = normalize_omdb_rating(omdb_data) if omdb_data else []
        if tv.vote_average is not None:
            scores.append(
                MediaScore(
                    source=MediaExternalSource.TMDB.value,
                    value=tv.vote_average,
                    vote_count=tv.vote_count,
                )
            )
        tv_detailed.media_scores = scores
        return tv_detailed

    @staticmethod
    def to_anime_detailed(
        anime: AnilistMediaDetailed, omdb_data: Optional[OMDbData] = None
    ) -> AnimeDetailed:
        anime_detailed = AnilistNormalizer.normalize_anime_detailed(anime)
        scores = normalize_omdb_rating(omdb_data) if omdb_data else []
        if anime.average_score is not None:
            scores.append(
                MediaScore(
                    source=MediaExternalSource.ANILIST.value,
                    value=anime.average_score,
                )
            )
        anime_detailed.media_scores = scores
        return anime_detailed

    @staticmethod
    def to_manga_detailed(
        manga: AnilistMediaDetailed, omdb_data: Optional[OMDbData] = None
    ) -> MangaDetailed:
        manga_detailed = AnilistNormalizer.normalize_manga_detailed(manga)
        scores = normalize_omdb_rating(omdb_data) if omdb_data else []
        if manga.average_score is not None:
            scores.append(
                MediaScore(
                    source=MediaExternalSource.ANILIST.value,
                    value=manga.average_score,
                )
            )
        manga_detailed.media_scores = scores
        return manga_detailed
