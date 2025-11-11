from typing import List
from app.models.anilist_models import Anilist_Media
from app.integrations.anilistApi import AnilistApi

import logging

logger = logging.getLogger(__name__)

class AnilistService:
    def __init__(self):
        self.anilist_api = AnilistApi()

    async def search_anime(self, search: str, page: int = 1, per_page: int = 10) -> dict:  # Updated return type for clarity
        animes, page_info = await self.anilist_api.get_anime(search, page, per_page)

        return {
            "results": animes,
            "page": page_info.get("currentPage", page),
            "perPage": per_page,
            "hasNextPage": page_info.get("hasNextPage", False)
        }

    async def search_comic(self, search: str, page: int = 1, per_page: int = 10) -> dict:  # Updated to match search_anime
        comics, page_info = await self.anilist_api.get_comic(search, page, per_page)  # Updated call

        return {  # Updated return to dict with pagination info
            "results": comics,
            "page": page_info.get("currentPage", page),
            "perPage": per_page,
            "hasNextPage": page_info.get("hasNextPage", False)
        }

    async def get_user_media_list(self, id_in: List[int]) -> List[Anilist_Media]:
        media_list = await self.anilist_api.get_media_list_by_id_list(id_in)

        return media_list

    