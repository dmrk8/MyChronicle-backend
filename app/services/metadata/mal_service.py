

from app.integrations.mal_api import MALApi
from app.models.providers.mal_models import MALAnimeData, MALMangaData


class MALService:
    def __init__(self, mal_api: MALApi):
        self.mal_api = mal_api

    async def get_anime_details(self, mal_id: int) -> MALAnimeData:
        return await self.mal_api.get_anime_details(mal_id)

    async def get_manga_details(self, mal_id: int) -> MALMangaData:
        return await self.mal_api.get_manga_details(mal_id)
