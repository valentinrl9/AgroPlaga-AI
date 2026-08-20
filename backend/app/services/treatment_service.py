from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.data.crop_catalog import normalize_crop, resolve_crop_name
from app.models.biocide_product import BiocideProduct
from app.models.farm import Farm
from app.models.farm_treatment import FarmTreatment
from app.models.scan import Scan
from app.models.user import User
from app.schemas.treatment import BiocideProductRead, DoseCalculateRequest, DoseCalculateResponse, TreatmentCreate, TreatmentRead
from app.services.scan_validation import is_scan_rejected, is_scan_verified, verification_label

_BIO_KEYWORDS = (
    "bacillus",
    "trichoderma",
    "beauveria",
    "metarhizium",
    "steinernema",
    "saccharomyces",
    "extracto",
    "fermentado",
    "microorganismo",
    "micorriza",
    "vacciplant",
)


def crop_match_keys(crop: str) -> set[str]:
    raw = crop.strip().lower()
    keys = {raw, normalize_crop(crop)}
    resolved = resolve_crop_name(crop)
    if resolved:
        keys.add(resolved.lower())
        keys.add(normalize_crop(resolved))
    return {k for k in keys if k}


def is_biological_product(product: BiocideProduct) -> bool:
    blob = " ".join(
        filter(
            None,
            [product.active_substance or "", product.agent_name or "", product.name or ""],
        )
    ).lower()
    return any(keyword in blob for keyword in _BIO_KEYWORDS)


def biocide_to_read(product: BiocideProduct) -> BiocideProductRead:
    return BiocideProductRead(
        id=product.id,
        registry_no=product.registry_no,
        name=product.name,
        active_substance=product.active_substance,
        plague=product.plague,
        crop=product.crop,
        dose_min_l_ha=product.dose_min_l_ha,
        dose_max_l_ha=product.dose_max_l_ha,
        dose_unit=product.dose_unit,
        agent_name=product.agent_name,
        safety_hours=product.safety_hours,
        source=product.source,
        is_biological=is_biological_product(product),
    )


def list_biocides(db: Session, plague: str, crop: str) -> list[BiocideProductRead]:
    plague_key = plague.strip().lower()
    crop_keys = crop_match_keys(crop)
    rows = (
        db.query(BiocideProduct)
        .filter(
            BiocideProduct.plague == plague_key,
            BiocideProduct.crop.in_(crop_keys),
            func.lower(BiocideProduct.product_status) == "vigente",
        )
        .order_by(BiocideProduct.name.asc())
        .all()
    )
    reads = [biocide_to_read(row) for row in rows]
    reads.sort(key=lambda item: (not item.is_biological, item.name.lower()))
    return reads


def get_biocide_product(db: Session, registry_no: str, plague: str, crop: str) -> BiocideProduct | None:
    crop_keys = crop_match_keys(crop)
    return (
        db.query(BiocideProduct)
        .filter(
            BiocideProduct.registry_no == registry_no.strip(),
            BiocideProduct.plague == plague.strip().lower(),
            BiocideProduct.crop.in_(crop_keys),
        )
        .first()
    )


def calculate_dose(db: Session, payload: DoseCalculateRequest) -> DoseCalculateResponse:
    if payload.plague and payload.crop:
        product = get_biocide_product(db, payload.registry_no, payload.plague, payload.crop)
    else:
        product = db.query(BiocideProduct).filter(BiocideProduct.registry_no == payload.registry_no.strip()).first()
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

    scan: Scan | None = None
    if payload.scan_id is not None:
        scan = db.query(Scan).filter(Scan.id == payload.scan_id, Scan.user_id == user.id).first()
        if not scan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escaneo no encontrado")
        if is_scan_rejected(scan):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Este escaneo fue rechazado por el perito. "
                    "Realiza un nuevo escaneo o consulta con tu técnico antes de registrar un tratamiento."
                ),
            )
        if not is_scan_verified(scan) and not payload.ack_unverified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Plaga no validada por perito. Confirma ack_unverified=true "
                    "para registrar bajo tu responsabilidad."
                ),
            )

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
        elif scan and not is_scan_verified(scan) and user.has_siex_enterprise:
            siex_message = (
                "Tratamiento registrado. El cuaderno SIEX de cooperativa requiere un escaneo validado por el perito."
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
            elif scan and not is_scan_verified(scan):
                siex_message = (
                    "Tratamiento registrado. Entrada SIEX omitida: plaga no validada por perito."
                )

    result = _treatment_read(row)
    result.siex_entry_id = siex_entry_id
    result.siex_message = siex_message
    result.scan_verification = verification_label(scan)
    return result


def list_active_treatments(db: Session, user_id: int, farm_id: int | None = None) -> list[TreatmentRead]:
    query = db.query(FarmTreatment).filter(FarmTreatment.user_id == user_id, FarmTreatment.status == "active")
    if farm_id is not None:
        query = query.filter(FarmTreatment.farm_id == farm_id)
    rows = query.order_by(FarmTreatment.applied_at.desc()).all()
    return [_treatment_read(r) for r in rows]
