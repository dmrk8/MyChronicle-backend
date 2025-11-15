from typing import List, Optional
from app.services.anilist_service import AnilistService
from app.repositories.review_repository import ReviewsCRUD
from app.models.user_models import UserData

class LibraryService:
    def __init__(self, collection_name):
        self.anilist_service = AnilistService()
        self.user_repo = ReviewsCRUD(collection_name)
         
    async def get_user_reviews(self, user: UserData, 
                                page: int,
                                per_page: int,
                                title: str,
                                sort_by: str,
                                sort_order: int,
                                ):
        if not user.id:
            raise ValueError("User ID cannot be None.") 
        
        filters = self.set_filters("title", title)
        
        #get filtered reviews
        user_reviews = self.user_repo.get_reviews(user.id, filters, page, per_page, sort_by, sort_order)

        media_ids = [r.media_id for r in user_reviews]

        media_list = await self.anilist_service.get_user_media_list(media_ids)

        media_map = {item.media_id: item for item in media_list}
    
        
        total = self.user_repo.count_reviews_by_user(user.id, filters)
        
        return {
        "results": [],
        "page": page,
        "per_page": per_page,
        "total": total,
        "has_next_page": page * per_page < total
    }
        
    def set_filters(self, param_name: str, param_value: Optional[str]) -> dict:
        filters = {}
        if param_value:  
            filters[param_name] = {"$regex": param_value, "$options": "i"}  
        return filters
    
    
                          