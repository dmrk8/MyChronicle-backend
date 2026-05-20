from datetime import datetime
from datetime import timezone
from typing import List, Optional


from app.models.shared.media import MediaScore, MediaScoreSource


from app.models.providers.omdb_models import OMDbData


class OMDbNormalizer:
    @staticmethod
    def parse_vote_count(votes: str | None) -> int | None:
        if votes is None:
            return None
        try:
            return int(votes.replace(",", ""))
        except Exception:
            return None

    @staticmethod
    def normalize_score_value(v) -> float:
        """
        Normalize a score value to a float in the 0–100 range.
        Accepts strings like "7.4/10", "66%", "7.4", or numeric input.
        Always returns a value out of 100.
        """
        if isinstance(v, str):
            v = v.strip()

            # "7.4/10" → 74
            if "/" in v:
                num, denom = v.split("/")
                return (float(num) / float(denom)) * 100

            # "66%" → 66
            if v.endswith("%"):
                return float(v.replace("%", ""))

            # "7.4" → assume /10 → 74
            val = float(v)
            if val <= 10:
                return val * 10
            return val  # Already out of 100

        # numeric input
        if isinstance(v, (int, float)):
            if v <= 10:
                return float(v) * 10
            return float(v)  # Already out of 100

        raise ValueError(f"Invalid score: {v}")

    @staticmethod
    def normalize_omdb_rating(omdb_data: OMDbData) -> List[MediaScore]:
        scores = []
        if omdb_data and omdb_data.Ratings:
            for rating in omdb_data.Ratings:
                if rating.Source == "Internet Movie Database":
                    scores.append(
                        MediaScore(
                            value=OMDbNormalizer.normalize_score_value(rating.Value),
                            source=MediaScoreSource.IMDB,
                            vote_count=OMDbNormalizer.parse_vote_count( # type: ignore
                                omdb_data.imdb_votes
                            ),
                        )
                    )
                elif rating.Source == "Rotten Tomatoes":
                    scores.append(
                        MediaScore(
                            value=OMDbNormalizer.normalize_score_value(rating.Value),
                            source=MediaScoreSource.ROTTEN_TOMATOES,
                            voteCount=None
                        ) 
                    )

                elif rating.Source == "Metacritic":
                    scores.append(
                        MediaScore(
                            value=OMDbNormalizer.normalize_score_value(rating.Value),
                            source=MediaScoreSource.METACRITIC,
                            voteCount=None
                        )
                    )
                else:
                    continue

        return scores

    @staticmethod
    def parse_released(release_date: Optional[str]) -> Optional[datetime]:
        """
        Convert OMDb's Released date string to a datetime object.
        OMDb dates are typically in the format "01 Jan 2000".
        """
        if not release_date:
            return None

        try:
            return datetime.strptime(release_date, "%d %b %Y").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            return None

    @staticmethod
    def parse_end_year(year: str) -> Optional[int]:
        """
        Extract the end year from OMDb's Year field.
        The Year field can be in formats like "1999", "1999–2003", "1999–".
        This function returns the end year as an integer, or None if it cannot be determined.
        """
        if not year:
            return None

        # "2013–2023" -> 2023
        try:
            return int(year.split("–")[-1].strip())
        except (ValueError, IndexError):
            return None
