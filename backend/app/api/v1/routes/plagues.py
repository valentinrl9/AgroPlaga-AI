from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_active_user
from app.data.plague_catalog import catalog_entries, load_catalog
from app.models.user import User
from app.schemas.official_source import OfficialSourceRef, OfficialSourcesResponse
from app.services.official_sources_service import resolve_official_sources

router = APIRouter()


@router.get("")
def list_plagues(_current_user: User = Depends(get_current_active_user)):
    catalog = load_catalog()
    return {
        "version": catalog["version"],
        "region": catalog["region"],
        "labels": catalog["labels"],
        "plagues": catalog_entries(),
    }


@router.get("/official-sources", response_model=OfficialSourcesResponse)
def official_sources(
    plague: str = Query(..., min_length=2),
    crop: str | None = Query(default=None),
    context: str = Query(default="recommendation", pattern="^(recommendation|alert|treatment)$"),
    _current_user: User = Depends(get_current_active_user),
):
    sources = resolve_official_sources(
        plague=plague,
        crop=crop,
        context=context,
        include_orientation=context == "recommendation",
        include_community=context == "alert",
    )
    return OfficialSourcesResponse(
        plague=plague.strip().lower(),
        crop=crop,
        context=context,
        sources=[OfficialSourceRef(**item) for item in sources],
    )
