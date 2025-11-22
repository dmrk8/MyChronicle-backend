import httpx
from dotenv import load_dotenv
import os
import logging
from app.models.tmdb_models import TMDB_Search_Movie, TMDBPagination

load_dotenv()

logger = logging.getLogger(__name__)

class TMDBApi:
    BASE_URL = "https://api.themoviedb.org/3/search/movie"
    
    @property
    def HEADERS(self):
        token = os.getenv("TMDB_ACCESS_TOKEN")
        return {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
    async def search_movie(self,
                           page: int,
                           query: str,
                           language: str = "en-US", #language of the query results
                           include_adult: bool = False #amateur porn like JAVs
                           ) -> TMDBPagination:
        logger.info(f"Searching movies for query: '{query}', page: {page}, language: {language}, include_adult: {include_adult}")
        params = {
            "query" : query,
            "language" : language,
            "page" : page,
            "include_adult" : str(include_adult).lower()
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, headers=self.HEADERS, params=params)
            response.raise_for_status()
            try:
                data = response.json()
                movies = []
                for movie_data in data['results']:
                    movies.append(self.map_movie_search_results(movie_data))
                
                logger.info(f"Successfully retrieved {len(movies)} movies from page {data.get('page', 1)} of {data.get('total_pages', 1)}")
                return TMDBPagination(
                    results=movies,
                    page=data.get('page', 1),
                    total_pages=data.get('total_pages', 1),
                    total_results=data.get('total_results', 0)
                )
            except Exception as e:
                logger.error(f"Error processing API response for query '{query}': {e}")
                raise ValueError(f"Invalid API response: {e}")
    
    def map_movie_search_results(self,
                                 data
                                 ) -> TMDB_Search_Movie:
        return TMDB_Search_Movie.model_validate(data)