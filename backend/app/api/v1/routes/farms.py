from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user
from app.models.farm import Farm
from app.models.user import User
from app.models.zone import AgriZone
from app.models.climate_station import ClimateStation
from app.schemas.farm import FarmCreate, FarmRead, FarmUpdate
from app.siex.service import validate_sigpac

router = APIRouter()


@router.get("", response_model=list[FarmRead])
def list_farms(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Farm)
        .filter(Farm.user_id == current_user.id)
        .order_by(Farm.created_at.desc())
        .all()
    )


@router.post("", response_model=FarmRead, status_code=status.HTTP_201_CREATED)
def create_farm(
    body: FarmCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if body.zone_id is not None:
        zone = db.query(AgriZone).filter(AgriZone.id == body.zone_id).first()
        if not zone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zona no encontrada")

    sigpac = None
    if body.sigpac_code:
        sigpac = validate_sigpac(body.sigpac_code)

    farm = Farm(
        user_id=current_user.id,
        name=body.name.strip(),
        crop=body.crop.strip(),
        farm_type=body.farm_type,
        zone_id=body.zone_id,
        nave=body.nave.strip() if body.nave else None,
        sector=body.sector.strip() if body.sector else None,
        crop_stage=body.crop_stage.strip() if body.crop_stage else None,
        crop_variant=body.crop_variant.strip() if body.crop_variant else None,
        surface_m2=body.surface_m2,
        sigpac_code=sigpac,
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@router.patch("/{farm_id}", response_model=FarmRead)
def update_farm(
    farm_id: int,
    body: FarmUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finca no encontrada")

    if body.name is not None:
        farm.name = body.name.strip()
    if body.crop is not None:
        farm.crop = body.crop.strip()
    if body.zone_id is not None:
        zone = db.query(AgriZone).filter(AgriZone.id == body.zone_id).first()
        if not zone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zona no encontrada")
        farm.zone_id = body.zone_id
    if body.nave is not None:
        farm.nave = body.nave.strip() or None
    if body.sector is not None:
        farm.sector = body.sector.strip() or None
    if body.crop_stage is not None:
        farm.crop_stage = body.crop_stage.strip() or None
    if body.crop_variant is not None:
        farm.crop_variant = body.crop_variant.strip() or None
    if body.surface_m2 is not None:
        farm.surface_m2 = body.surface_m2
    if body.sigpac_code is not None:
        farm.sigpac_code = validate_sigpac(body.sigpac_code) if body.sigpac_code.strip() else None
    if "climate_station_id" in body.model_fields_set:
        if body.climate_station_id is None:
            farm.climate_station_id = None
        else:
            station = (
                db.query(ClimateStation)
                .filter(ClimateStation.id == body.climate_station_id, ClimateStation.active.is_(True))
                .first()
            )
            if station is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estación meteorológica no encontrada")
            farm.climate_station_id = station.id

    db.commit()
    db.refresh(farm)
    return farm


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(
    farm_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finca no encontrada")
    db.delete(farm)
    db.commit()
