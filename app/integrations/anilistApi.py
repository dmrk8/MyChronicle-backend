from typing import Any, List, Tuple
import httpx

from app.models.anilist_models import Anilist_Media
from app.extensions.anilist_cache import anilits_cache

ANILIST_URL = "https://graphql.anilist.co"

class AnilistApi:
    def __init__(self):
        pass

    # @anilits_cache(ttl=300, model=Anilist_Media, is_list=True)
    async def get_anime(self, query: str, page: int = 1, per_Page: int = 10) -> Tuple[List[Anilist_Media], Any]:
        graphql_query = {
            "query": """
            query($search: String, $perPage: Int, $page: Int) {
                Page(perPage: $perPage, page: $page) {
                    pageInfo {
                        total
                        currentPage
                        lastPage
                        hasNextPage
                    }
                    media(type: ANIME, search: $search) {
                        id
                        title {
                            english
                            native
                            romaji
                        }
                        synonyms
                        coverImage {
                            large
                        }
                        description
                        startDate {
                            year
                        }
                        endDate {
                            year
                        }
                        type
                        duration
                        status
                        genres
                        countryOfOrigin
                        format
                        meanScore
                        tags {
                            name
                        }
                    }
                }
            }
            """,
            "variables": {
                "search": query,
                "perPage": per_Page,
                "page": page
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(ANILIST_URL, json=graphql_query)
            response.raise_for_status()
            data = response.json()

        media_list = map_anilist_to_media(data)
        page_info = data.get("data", {}).get("Page", {}).get("pageInfo", {})

        return media_list, page_info

    # @anilits_cache(ttl=300, model=Anilist_Media, is_list=True)
    async def get_comic(self, query: str, page: int = 1, per_Page: int = 10) -> Tuple[List[Anilist_Media], Any]:
        graphql_query = {
            "query": """
            query($search: String, $perPage: Int, $page: Int) {
                Page(perPage: $perPage, page: $page) {
                    pageInfo {
                        total
                        currentPage
                        lastPage
                        hasNextPage
                    }
                    media(type: MANGA, search: $search) {
                        id
                        title {
                            english
                            native
                            romaji
                        }
                        synonyms
                        coverImage {
                            large
                        }
                        description
                        startDate {
                            year
                        }
                        endDate {
                            year
                        }
                        type
                        duration
                        status
                        genres
                        countryOfOrigin
                        format
                        meanScore
                        tags {
                            name
                        }
                    }
                }
            }
            """,
            "variables": {
                "search": query,
                "perPage": per_Page,
                "page": page
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(ANILIST_URL, json=graphql_query)
            response.raise_for_status()
            data = response.json()

        media_list = map_anilist_to_media(data)
        page_info = data.get("data", {}).get("Page", {}).get("pageInfo", {})

        return media_list, page_info

    async def get_media_list_by_id_list(self, id_in: List[int]) -> List[Anilist_Media]:
        graphql_query = {
            "query": """
            query Page($idIn: [Int]) {
                Page(perPage: 50) {
                    media(id_in: $idIn) {
                        id
                        title {
                            english
                            native
                            romaji
                        }
                        synonyms
                        coverImage {
                            large
                        }
                        description
                        startDate {
                            year
                        }
                        endDate {
                            year
                        }
                        type
                        duration
                        status
                        genres
                        countryOfOrigin
                        format
                        meanScore
                        tags {
                            name
                        }
                    }
                }
            }
            """,
            "variables": {
                "idIn": id_in
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(ANILIST_URL, json=graphql_query)
            response.raise_for_status()
            data = response.json()

        return map_anilist_to_media(data)

def map_anilist_to_media(response: dict) -> List[Anilist_Media]:
    media_list = response.get("data", {}).get("Page", {}).get("media", [])
    return [
        Anilist_Media(
            media_id=item.get("id"),
            title=item.get("title", {}),
            synonyms=item.get("synonyms", []),
            cover_image=item.get("coverImage", {}).get("large"),
            description=item.get("description"),
            start_year=item.get("startDate", {}).get("year"),
            end_year=item.get("endDate", {}).get("year"),
            type=item.get("type"),
            duration=item.get("duration"),
            status=item.get("status"),
            genres=item.get("genres"),
            country_of_origin=item.get("countryOfOrigin"),
            format=item.get("format"),
            mean_score=item.get("meanScore"),
            tags=item.get("tags", []),
        )
        for item in media_list
    ]