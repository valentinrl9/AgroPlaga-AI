from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_admin, get_current_active_user
from app.mapa.etl import get_etl_status, run_mapa_etl
from app.mapa.repository import count_mapa_products, latest_sync_at
from app.models.user import User
from app.schemas.treatment import (
    BiocideProductRead,
    CatalogStatusRead,
    DoseCalculateRequest,
    DoseCalculateResponse,
    TreatmentCreate,
    TreatmentRead,
)
from app.services import treatment_service

router = APIRouter()

MAPA_DISCLAIMER = (
    "Datos del Registro Oficial de Productos Fitosanitarios (MAPA). "
    "Orientación técnica — consulte la ficha oficial y la legislación vigente."
)


@router.get("/catalog/status", response_model=CatalogStatusRead)
def catalog_status(
    _user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    state = get_etl_status()
    synced = latest_sync_at(db)
    stale = False
    if synced:
        stale = datetime.now(timezone.utc) - synced > timedelta(days=30)
    return CatalogStatusRead(
        success=state.get("success"),
        synced_at=synced,
        catalog_date=state.get("catalog_date"),
        products_indexed=count_mapa_products(db),
        stale=stale,
        disclaimer=MAPA_DISCLAIMER,
    )


@router.post("/etl/run")
def etl_run(
    use_cache: bool = Query(default=False),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_active_admin),
):
    try:
        return run_mapa_etl(db, use_cache=use_cache)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/biocides", response_model=list[BiocideProductRead])
def list_biocides(
    plague: str = Query(...),
    crop: str = Query(...),
    _user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return treatment_service.list_biocides(db, plague=plague, crop=crop)


@router.post("/dose/calculate", response_model=DoseCalculateResponse)
def calculate_dose(
    payload: DoseCalculateRequest,
    _user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return treatment_service.calculate_dose(db, payload)


@router.post("", response_model=TreatmentRead, status_code=201)
def create_treatment(
    payload: TreatmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return treatment_service.create_treatment(db, current_user, payload)


@router.get("/active", response_model=list[TreatmentRead])
def list_active_treatments(
    farm_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return treatment_service.list_active_treatments(db, current_user.id, farm_id=farm_id)
