from datetime import datetime, timezone
from typing import Tuple

SEASONS = ["WINTER", "SPRING", "SUMMER", "FALL"]

def get_current_season(date: datetime | None = None) -> Tuple[str, int]:
    if date is None:
        date = datetime.now(timezone.utc)

    month = date.month
    year = date.year

    if month in (1, 2, 3):
        return "WINTER", year
    if month in (4, 5, 6):
        return "SPRING", year
    if month in (7, 8, 9):
        return "SUMMER", year
    return "FALL", year


def get_next_season(
    season: str,
    year: int,
) -> Tuple[str, int]:
    index = SEASONS.index(season)
    next_index = (index + 1) % len(SEASONS)

    next_season = SEASONS[next_index]
    next_year = year + 1 if season == "FALL" else year

    return next_season, next_year
