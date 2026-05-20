from fastapi import APIRouter, Depends

from app.core.dependencies import get_media_core_service
from app.core.exceptions import NotFoundException
from app.enums.media_enums import MediaType
from app.enums.media_enums import MediaExternalSource
from app.models.db.media_core_models import MediaCore
from app.services.media_core_service import MediaCoreService

media_core_router = APIRouter(prefix="/media-core", tags=["media-core"])


@media_core_router.get("/by-external-id", response_model=MediaCore)
async def get_media_core_by_external_id(
    primary_external_id: int,
    primary_external_source: str,
    media_type: str,
    service: MediaCoreService = Depends(get_media_core_service),
):
    external_source_enum = MediaExternalSource(primary_external_source.upper())
    media_type_enum = MediaType(media_type.upper())
    res = await service.get_media(
        primary_id=primary_external_id,
        external_source=external_source_enum,
        media_type=media_type_enum,
    )
    if not res:
        raise NotFoundException("Media not found")
    return MediaCore.model_validate(res.model_dump())
