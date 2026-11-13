from typing import Optional

from app.models.api.media_response_models import AnimeDetail, MangaDetail, MovieCollection, MovieDetail, TVDetail

from app.models.db.media_core_models import MediaDB
from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.mal_models import MALAnimeResponse, MALMangaResponse
from app.models.providers.omdb_models import OMDbData
from app.models.providers.tmdb_models import TMDBMovieDetail, TMDBTVDetail
from app.utils.normalizers.anilist_normalizer import AnilistNormalizer
from app.utils.normalizers.score_builder import ScoreBuilder
from app.utils.normalizers.tmdb_normalizer import TMDBNormalizer


class MediaResponseAssembler:
    @staticmethod
    def to_movie_detail(
        media_core: MediaDB,
        movie: TMDBMovieDetail,
        collection: Optional[MovieCollection] = None,
        omdb_data: Optional[OMDbData] = None,
    ) -> MovieDetail:
        movie_detail = TMDBNormalizer.normalize_movie_detail(movie)

        scores = ScoreBuilder.build_movie_or_tv_score(movie, omdb_data)

        movie_detail.scores = scores
 
        return MovieDetail(
            id = str(media_core.id),
            **movie_detail.model_dump(),
            collection=collection,
        )

    @staticmethod
    def to_tv_detail(
        media_core: MediaDB,
        tv: TMDBTVDetail, omdb_data: Optional[OMDbData] = None
    ) -> TVDetail:
        tv_detailed = TMDBNormalizer.normalize_tv_detail(tv)

        scores = ScoreBuilder.build_movie_or_tv_score(tv, omdb_data)
        tv_detailed.scores = scores

        return TVDetail(
            id=str(media_core.id),
            **tv_detailed.model_dump(),
        )

    @staticmethod
    def to_anime_detail(
        media_core: MediaDB,
        anime: AnilistMediaDetail,
        mal_data: Optional[MALAnimeResponse] = None,
    ) -> AnimeDetail:
        
        anime_detailed = AnilistNormalizer.normalize_anime_detail(anime)
        scores = ScoreBuilder.build_anime_or_manga_score(anime, mal_data)

        anime_detailed.scores = scores

        anime_detailed.background = (
            mal_data.data.background if mal_data and mal_data.data.background else None
        )
        return AnimeDetail(
            id=str(media_core.id),
            **anime_detailed.model_dump(),
        )

    @staticmethod
    def to_manga_detail(
        media_core: MediaDB,
        manga: AnilistMediaDetail, mal_data: Optional[MALMangaResponse] = None
    ) -> MangaDetail:
        manga_detailed = AnilistNormalizer.normalize_manga_detail(manga)
        scores = ScoreBuilder.build_anime_or_manga_score(manga, mal_data)

        manga_detailed.scores = scores
        
        manga_detailed.background = (
            mal_data.data.background if mal_data and mal_data.data.background else None
        )
        manga_detailed.authors = (
            [author.name for author in mal_data.data.authors]
            if mal_data and mal_data.data.authors
            else []
        )

        return MangaDetail(
            id=str(media_core.id),
            **manga_detailed.model_dump(),
        )
