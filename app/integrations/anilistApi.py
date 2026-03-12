from typing import Any, List, Optional, Tuple, Dict
from httpx import AsyncClient

from app.models.anilist_models import (
    AnilistMediaDetailed,
    AnilistMediaMinimal,
    AnilistPageInfo,
    AnilistFeaturedMediaResponse,
)
from app.enums.anilist_enums import SortOption
from app.integrations.http_helpers import perform_request

ANILIST_URL = "https://graphql.anilist.co"


class AnilistApi:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def get_featured_media(
        self,
        page: int,
        per_page: int,
        season: Optional[str],
        season_year: Optional[int],
        sort: str,
        media_type: str,
    ) -> List[AnilistMediaMinimal]:
        """
        Fetches featured media data: all time popular, trending now, popular this season, and upcoming next season.
        Uses the provided GraphQL query with different parameters for each category.
        """

        variables = {
            "page": page,
            "perPage": per_page,
            "sort": [sort],
            "type": media_type,
        }

        if season:
            variables["season"] = season
        if season_year:
            variables["seasonYear"] = season_year

        graphql_query = {
            "query": """ 
            query($page: Int, $perPage: Int, $type: MediaType, $sort: [MediaSort], $season: MediaSeason, $seasonYear: Int) {
              Page(page: $page, perPage: $perPage) {
                media(type: $type, sort: $sort, season: $season, seasonYear: $seasonYear) {
                  id
                  type
                  title {
                    english
                    romaji
                  }
                  format
                  genres
                  episodes
                  duration
                  status
                  nextAiringEpisode {
                    episode
                    airingAt
                    timeUntilAiring
                  }
                  studios {
                    edges {
                      isMain
                      node {
                        id
                        name
                      }
                    }
                  }
                  coverImage {
                    large
                    medium
                    extraLarge
                  }
                  season
                  seasonYear
                  averageScore
                }
              }
            }
            """,
            "variables": variables,
        }

        data = await perform_request(
            client=self.client,
            method="POST",
            url=ANILIST_URL,
            headers=None,
            params=None,
            graphql_query=graphql_query,
            action="get_featured_media",
        )

        media_list = data.get("data", {}).get("Page", {}).get("media", [])

        # Map each media item to AnilistMedia model using model_validate
        featured_media = []
        for media in media_list:

            featured_media.append(AnilistMediaMinimal.model_validate(media))

        return featured_media

    async def search_media(
        self,
        page: int,
        per_page: int,
        search: Optional[str],
        media_type: str,
        sort: str,
        season: Optional[str],
        season_year: Optional[int],
        format: Optional[str],
        status: Optional[str],
        genre_in: Optional[List[str]],
        tag_in: Optional[List[str]],
        is_adult: Optional[bool],
        country_of_origin: Optional[str],
        genre_not_in: Optional[List[str]],
        tag_not_in: Optional[List[str]],
    ) -> tuple[List[AnilistMediaMinimal], AnilistPageInfo]:
        """
        Searches for media based on the provided parameters.
        Uses the provided GraphQL query with filters for search.
        """

        variables = {
            "page": page,
            "perPage": per_page,
            "type": media_type,
            "sort": [sort],
            "search": search,
            "isAdult": is_adult,
        }

        if season:
            variables["season"] = season
        if season_year:
            variables["seasonYear"] = season_year
        if format:
            variables["format"] = format
        if status:
            variables["status"] = status
        if genre_in:
            variables["genreIn"] = genre_in
        if tag_in:
            variables["tagIn"] = tag_in
        if genre_not_in:
            variables["genreNotIn"] = genre_not_in
        if tag_not_in:
            variables["tagNotIn"] = tag_not_in
        if country_of_origin:
            variables["countryOfOrigin"] = country_of_origin

        graphql_query = {
            "query": """ 
            query($page: Int, $perPage: Int, $type: MediaType, $sort: [MediaSort], $season: MediaSeason, $seasonYear: Int, $format: MediaFormat, $status: MediaStatus, $genreIn: [String], $tagIn: [String], $search: String, $isAdult: Boolean, $countryOfOrigin: CountryCode, $genreNotIn: [String], $tagNotIn: [String]) {
              Page(page: $page, perPage: $perPage) {
                pageInfo {
                  currentPage
                  hasNextPage
                  perPage
                  total
                }
                media(type: $type, sort: $sort, season: $season, seasonYear: $seasonYear, format: $format, status: $status, genre_in: $genreIn, tag_in: $tagIn, search: $search, isAdult: $isAdult, countryOfOrigin: $countryOfOrigin, genre_not_in: $genreNotIn, tag_not_in: $tagNotIn) {
                  id
                  type
                  title {
                    english
                    romaji
                  }
                  format
                  genres
                  episodes
                  duration
                  status
                  nextAiringEpisode {
                    episode
                    airingAt
                    timeUntilAiring
                  }
                  studios {
                    edges {
                      isMain
                      node {
                        id
                        name
                      }
                    }
                  }
                  coverImage {
                    large
                    medium
                    extraLarge
                  }
                  season
                  seasonYear
                  averageScore
                  chapters
                  startDate {
                    year
                    day
                    month
                  }
                  endDate {
                    year
                    month
                    day
                  }
                }
              }
            }
            """,
            "variables": variables,
        }

        data = await perform_request(
            client=self.client,
            method="POST",
            url=ANILIST_URL,
            headers=None,
            params=None,
            graphql_query=graphql_query,
            action="search_media",
        )

        page_data = data.get("data", {}).get("Page", {})
        media_list = page_data.get("media", [])

        page_info = AnilistPageInfo.model_validate(page_data.get("pageInfo", {}))

        search_media = []
        for media in media_list:
            search_media.append(AnilistMediaMinimal.model_validate(media))

        return search_media, page_info

    async def get_media_detail(self, media_id: int) -> AnilistMediaDetailed:
        """
        Fetches detailed information for a specific media by ID.
        Uses the provided GraphQL query.
        """

        variables = {"mediaId": media_id}

        graphql_query = {
            "query": """
            query($mediaId: Int) {
              Media(id: $mediaId) {
                averageScore
                bannerImage
                chapters
                countryOfOrigin
                coverImage {
                  medium
                  large
                  extraLarge
                }
                description
                duration
                endDate {
                  day
                  month
                  year
                }
                episodes
                format
                genres
                isAdult
                nextAiringEpisode {
                  episode
                  airingAt
                  timeUntilAiring
                }
                relations {
                  edges {
                    relationType
                    node {
                      title {
                        english
                        romaji
                        native
                      }
                      format
                      id
                      status
                      coverImage {
                        extraLarge
                      }
                      type
                    }
                  }
                }
                season
                seasonYear
                source
                startDate {
                  day
                  month
                  year
                }
                status
                synonyms
                title {
                  english
                  native
                  romaji
                }
                type
                volumes
                tags {
                  name
                  isMediaSpoiler
                  isGeneralSpoiler
                  rank
                  description
                }
                studios {
                  edges {
                    isMain
                    node {
                      name
                      id
                    }
                  }
                }
                recommendations(sort: RATING_DESC, page: 1, perPage: 7) {
                  edges {
                    node {
                      mediaRecommendation {
                        id
                        title {
                          english
                          native
                          romaji
                        }
                        coverImage {
                          extraLarge
                        }
                        type
                      }
                    }
                  }
                }
                characters(sort: RELEVANCE, page: 1, perPage: 6) {
                  edges {
                    node {
                      image {
                        large
                      }
                      name {
                        full
                      }
                    }
                    voiceActors(language: JAPANESE) {
                      name {
                        full
                      }
                      image {
                        large
                      }
                    }
                    role
                  }
                }

                id
              }
            }
            """,
            "variables": variables,
        }

        data = await perform_request(
            client=self.client,
            method="POST",
            url=ANILIST_URL,
            headers=None,
            params=None,
            graphql_query=graphql_query,
            action="get_media_detail",
        )

        media = data.get("data", {}).get("Media", {})

        detailed_media = AnilistMediaDetailed.model_validate(media)

        return detailed_media

    async def get_featured_media_bulk(
        self,
        page: int,
        per_page: int,
        current_season: str,
        current_season_year: int,
        next_season: str,
        next_season_year: int,
        media_type: str,
    ) -> AnilistFeaturedMediaResponse:
        """
        Fetches featured media data: all time popular, trending now, popular this season, and upcoming next season.
        Uses the provided GraphQL query with different parameters for each category.
        """

        variables = {
            "page": page,
            "perPage": per_page,
            "type": media_type,
            "currentSeason": current_season,
            "currentSeasonYear": current_season_year,
            "nextSeason": next_season,
            "nextSeasonYear": next_season_year,
        }

        graphql_query = {
            "query": """
                query FeaturedAnime(
                  $page: Int
                  $perPage: Int
                  $type: MediaType
                  $currentSeason: MediaSeason
                  $currentSeasonYear: Int
                  $nextSeason: MediaSeason
                  $nextSeasonYear: Int
                ) {
                  trending: Page(page: $page, perPage: $perPage) {
                    media(type: $type, sort: TRENDING_DESC) {
                      ...mediaFields
                    }
                  }

                  popularSeason: Page(page: $page, perPage: $perPage) {
                    media(
                      type: $type
                      sort: POPULARITY_DESC
                      season: $currentSeason
                      seasonYear: $currentSeasonYear
                    ) {
                      ...mediaFields
                    }
                  }

                  upcoming: Page(page: $page, perPage: $perPage) {
                    media(
                      type: $type
                      sort: POPULARITY_DESC
                      season: $nextSeason
                      seasonYear: $nextSeasonYear
                    ) {
                      ...mediaFields
                    }
                  }

                  allTime: Page(page: $page, perPage: $perPage) {
                    media(type: $type, sort: POPULARITY_DESC) {
                      ...mediaFields
                    }
                  }
                }

                fragment mediaFields on Media {
                  id
                  type
                  title {
                    english
                    romaji
                  }
                  format
                  genres
                  episodes
                  duration
                  status
                  nextAiringEpisode {
                    episode
                    airingAt
                    timeUntilAiring
                  }
                  studios {
                    edges {
                      isMain
                      node {
                        id
                        name
                      }
                    }
                  }
                  coverImage {
                    large
                    medium
                    extraLarge
                  }
                  season
                  seasonYear
                  averageScore
                  bannerImage
                }
                """,
            "variables": variables,
        }

        data = await perform_request(
            client=self.client,
            method="POST",
            url=ANILIST_URL,
            headers=None,
            params=None,
            graphql_query=graphql_query,
            action="get_featured_media_bulk",
        )

        trending_results = data.get("data", {}).get("trending").get("media", [])
        popular_season_results = (
            data.get("data", {}).get("popularSeason").get("media", [])
        )
        upcoming_results = data.get("data", {}).get("upcoming").get("media", [])
        alltime_results = data.get("data", {}).get("allTime").get("media", [])

        trending = []
        for media in trending_results:
            trending.append(AnilistMediaMinimal.model_validate(media))

        popular_season = []
        for media in popular_season_results:
            popular_season.append(AnilistMediaMinimal.model_validate(media))

        upcoming = []
        for media in upcoming_results:
            upcoming.append(AnilistMediaMinimal.model_validate(media))

        all_time = []
        for media in alltime_results:
            all_time.append(AnilistMediaMinimal.model_validate(media))

        return AnilistFeaturedMediaResponse(
            allTime=all_time,
            popularSeason=popular_season,
            trending=trending,
            upcoming=upcoming,
        )

    async def get_featured_manga_bulk(
        self,
        page: int,
        per_page: int,
        media_type: str,
    ) -> AnilistFeaturedMediaResponse:
        """
        Fetches featured manga data: trending, all time popular, and all time popular Manhwa.
        """
        variables = {
            "page": page,
            "perPage": per_page,
            "type": media_type,
        }

        graphql_query = {
            "query": """
                query FeaturedAnime(
                  $page: Int
                  $perPage: Int
                  $type: MediaType
                ) {
                  trending: Page(page: $page, perPage: $perPage) {
                    media(type: $type, sort: TRENDING_DESC) {
                      ...mediaFields
                    }
                  }
                  Alltime: Page(page: $page, perPage: $perPage) {
                    media(type: $type, sort: POPULARITY_DESC) {
                      ...mediaFields
                    }
                  }
                  AlltimeManhwa: Page(page: $page, perPage: $perPage) {
                    media(type: $type, sort: POPULARITY_DESC, countryOfOrigin: KR) {
                      ...mediaFields
                    }
                  }
                }
                fragment mediaFields on Media {
                  id
                  type
                  title {
                    english
                    romaji
                  }
                  format
                  genres
                  status
                  coverImage {
                    large
                    medium
                    extraLarge
                  }
                  bannerImage
                  averageScore
                }
            """,
            "variables": variables,
        }

        data = await perform_request(
            client=self.client,
            method="POST",
            url=ANILIST_URL,
            headers=None,
            params=None,
            graphql_query=graphql_query,
            action="get_featured_manga_bulk",
        )

        trending_results = data.get("data", {}).get("trending").get("media", [])
        alltime_results = data.get("data", {}).get("Alltime").get("media", [])
        alltime_manhwa_results = (
            data.get("data", {}).get("AlltimeManhwa").get("media", [])
        )

        trending = []
        for media in trending_results:
            trending.append(AnilistMediaMinimal.model_validate(media))

        all_time = []
        for media in alltime_results:
            all_time.append(AnilistMediaMinimal.model_validate(media))

        all_time_manhwa = []
        for media in alltime_manhwa_results:
            all_time_manhwa.append(AnilistMediaMinimal.model_validate(media))

        return AnilistFeaturedMediaResponse(
            trending=trending, allTime=all_time, allTimeManhwa=all_time_manhwa
        )
