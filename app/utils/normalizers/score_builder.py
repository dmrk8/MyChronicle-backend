from typing import List, Optional

from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.mal_models import MALAnimeResponse, MALMangaResponse
from app.models.providers.omdb_models import OMDbData
from app.models.providers.tmdb_models import TMDBMovieDetail, TMDBTVDetail
from app.models.shared.media import MediaScore, MediaScoreSource
from app.utils.normalizers.omdb_normalizer import OMDbNormalizer


class ScoreBuilder:
    @staticmethod
    def build_anime_or_manga_score(
        media: AnilistMediaDetail,
        mal_data: Optional[MALAnimeResponse | MALMangaResponse],
    ) -> Optional[List[MediaScore]]:
        scores = []

        if media.average_score:
            scores.append(
                MediaScore(
                    value=float(media.average_score),
                    source=MediaScoreSource.ANILIST,
                    vote_count=None
                )
            )
        if mal_data and mal_data.data.score:
            scores.append(
                MediaScore(
                    value=float(mal_data.data.score) * 10,
                    source=MediaScoreSource.MAL,
                    vote_count=mal_data.data.scored_by,
                )
            )
        return scores

    @staticmethod
    def build_movie_or_tv_score(
        media: TMDBMovieDetail | TMDBTVDetail, omdb_data: Optional[OMDbData]
    ) -> Optional[List[MediaScore]]:
        scores = OMDbNormalizer.normalize_omdb_rating(omdb_data) if omdb_data else []

        if media.vote_average:
            scores.append(
                MediaScore(
                    value=float(media.vote_average) * 10,
                    source=MediaScoreSource.TMDB,
                    vote_count=media.vote_count,
                )
            )
        

        return scores
