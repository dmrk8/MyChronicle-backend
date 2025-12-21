from cachetools import TTLCache

from app.utils.anilist_seasons import get_current_season, get_next_season

season_cache = TTLCache(maxsize=1, ttl=60*60*12)

def get_season_context():
    if "season" in season_cache:
        return season_cache["season"]

    current_season, current_year = get_current_season()
    next_season, next_year = get_next_season(current_season, current_year)

    season_cache["season"] = {
        "currentSeason": current_season,
        "currentSeasonYear": current_year,
        "nextSeason": next_season,
        "nextSeasonYear": next_year,
    }

    return season_cache["season"]
