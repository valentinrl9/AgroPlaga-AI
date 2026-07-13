from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.biocide_product import BiocideProduct
from app.models.farm import Farm
from app.models.farm_treatment import FarmTreatment
from app.models.user import User
from app.schemas.treatment import DoseCalculateRequest, DoseCalculateResponse, TreatmentCreate, TreatmentRead


def list_biocides(db: Session, plague: str, crop: str) -> list[BiocideProduct]:
    plague_key = plague.strip().lower()
    crop_key = crop.strip().lower()
    return (
        db.query(BiocideProduct)
        .filter(
            BiocideProduct.plague == plague_key,
            BiocideProduct.crop == crop_key,
            BiocideProduct.product_status == "vigente",
        )
        .order_by(BiocideProduct.name.asc())
        .all()
    )


def calculate_dose(db: Session, payload: DoseCalculateRequest) -> DoseCalculateResponse:
    query = db.query(BiocideProduct).filter(BiocideProduct.registry_no == payload.registry_no.strip())
    if payload.plague:
        query = query.filter(BiocideProduct.plague == payload.plague.strip().lower())
    if payload.crop:
        query = query.filter(BiocideProduct.crop == payload.crop.strip().lower())
    product = query.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado en catálogo MAPA")

    ha = payload.surface_m2 / 10000.0
    dose_l_ha = (product.dose_min_l_ha + product.dose_max_l_ha) / 2.0
    liters = ha * dose_l_ha * (payload.caldo_l_ha / 1000.0)
    dose_ml = round(liters * 1000.0, 1)

    return DoseCalculateResponse(
        registry_no=product.registry_no,
        product_name=product.name,
        dose_l_ha=round(dose_l_ha, 3),
        dose_ml=dose_ml,
        safety_hours=product.safety_hours,
    )


def _treatment_read(row: FarmTreatment) -> TreatmentRead:
    now = datetime.now(timezone.utc)
    applied = row.applied_at
    if applied.tzinfo is None:
        applied = applied.replace(tzinfo=timezone.utc)
    ends = applied + timedelta(hours=row.safety_hours)
    remaining = (ends - now).total_seconds() / 3600.0
    active = remaining > 0 and row.status == "active"
    return TreatmentRead(
        id=row.id,
        farm_id=row.farm_id,
        scan_id=row.scan_id,
        product_name=row.product_name,
        registry_number=row.registry_number,
        active_substance=row.active_substance,
        applied_at=row.applied_at,
        safety_hours=row.safety_hours,
        dose_ml=row.dose_ml,
        notes=row.notes,
        status="active" if active else "expired",
        hours_remaining=round(max(remaining, 0.0), 1) if active else 0.0,
        harvest_allowed=not active,
    )


def create_treatment(db: Session, user: User, payload: TreatmentCreate) -> TreatmentRead:
    farm: Farm | None = None
    if payload.farm_id is not None:
        farm = db.query(Farm).filter(Farm.id == payload.farm_id, Farm.user_id == user.id).first()
        if not farm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finca no encontrada")

    row = FarmTreatment(
        user_id=user.id,
        farm_id=payload.farm_id,
        scan_id=payload.scan_id,
        product_name=payload.product_name.strip(),
        registry_number=payload.registry_number,
        active_substance=payload.active_substance,
        applied_at=datetime.now(timezone.utc),
        safety_hours=payload.safety_hours,
        dose_ml=payload.dose_ml,
        notes=payload.notes,
        status="active",
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    siex_entry_id = None
    siex_message = None
    from app.siex import service as siex_service

    if siex_service.user_has_siex_access(user):
        if farm is None or not farm.sigpac_code:
            siex_message = (
                "Tratamiento registrado. Para cuaderno SIEX, vincula una finca con código SIGPAC del recinto."
            )
        else:
            entry = siex_service.compile_from_treatment(db, user, row)
            if entry:
                siex_entry_id = entry.id
                siex_message = (
                    "Entrada SIEX generada."
                    if entry.status == "registrado"
                    else "Entrada SIEX enviada a validación del perito."
                )

    result = _treatment_read(row)
    result.siex_entry_id = siex_entry_id
    result.siex_message = siex_message
    return result


def list_active_treatments(db: Session, user_id: int, farm_id: int | None = None) -> list[TreatmentRead]:
    query = db.query(FarmTreatment).filter(FarmTreatment.user_id == user_id, FarmTreatment.status == "active")
    if farm_id is not None:
        query = query.filter(FarmTreatment.farm_id == farm_id)
    rows = query.order_by(FarmTreatment.applied_at.desc()).all()
    return [_treatment_read(r) for r in rows]
