from app.integrations.jikan_api import JikanAPI
from app.models.providers.mal_models import MALAnimeResponse, MALMangaResponse


class JikanService:
    def __init__(self, jikan_api: JikanAPI):
        self.jikan_api = jikan_api

    async def get_anime_details(self, mal_id: int) -> MALAnimeResponse:
        return await self.jikan_api.get_anime_details(mal_id)

    async def get_manga_details(self, mal_id: int) -> MALMangaResponse:
        return await self.jikan_api.get_manga_details(mal_id)
