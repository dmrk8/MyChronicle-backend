from typing import List, Optional

from app.enums.media_enums import MediaExternalSource
from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.omdb_models import OMDbData
from app.models.providers.tmdb_models import TMDBMovieDetail, TMDBTVDetail
from app.models.db.media_db_models import MediaScore
from app.utils.normalizers.omdb_normalizer import OMDbNormalizer


class ScoreBuilder:
    @staticmethod
    def build_anilist_score(media: AnilistMediaDetail) -> Optional[List[MediaScore]]:
        scores = []

        if media.average_score is not None:
            scores.append(
                MediaScore(
                    value=float(media.average_score),
                    source=MediaExternalSource.ANILIST,
                )
            )
        return scores

    @staticmethod
    def build_tmdb_score(
        media: TMDBMovieDetail | TMDBTVDetail, omdb_data: Optional[OMDbData]
    ) -> Optional[List[MediaScore]]:
        scores = OMDbNormalizer.normalize_omdb_rating(omdb_data) if omdb_data else []

        if media.vote_average is not None:
            scores.append(
                MediaScore(
                    value=float(media.vote_average),
                    source=MediaExternalSource.TMDB,
                    vote_count=media.vote_count,
                )
            )

        return scores
