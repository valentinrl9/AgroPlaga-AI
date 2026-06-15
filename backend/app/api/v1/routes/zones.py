from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.zone import AgriZone
from app.schemas.zone import ZoneRead

router = APIRouter()


@router.get("", response_model=list[ZoneRead])
def list_zones(
    _current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(
            AgriZone.id,
            AgriZone.sigpac_code,
            AgriZone.name,
            AgriZone.province,
            AgriZone.municipality_code,
            func.ST_Y(AgriZone.centroid).label("lat"),
            func.ST_X(AgriZone.centroid).label("lon"),
        )
        .order_by(AgriZone.name)
        .all()
    )
    return [
        ZoneRead(
            id=row.id,
            sigpac_code=row.sigpac_code,
            name=row.name,
            province=row.province,
            municipality_code=row.municipality_code,
            lat=float(row.lat),
            lon=float(row.lon),
        )
        for row in rows
    ]
