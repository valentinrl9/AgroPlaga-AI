"""Compilación automática del cuaderno SIEX desde tratamientos."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.climate import service as climate_service
from app.models.farm import Farm
from app.models.farm_treatment import FarmTreatment
from app.models.scan import Scan
from app.models.siex_entry import SiexCuadernoEntry
from app.models.user import User
from app.models.zone import AgriZone
from app.schemas.siex import SiexEntryRead, SiexEntryValidate
from app.siex.config import SIEX_PREVIEW_OPEN
from app.services.scan_validation import effective_plague, is_scan_verified

_SIGPAC_RE = re.compile(r"^[A-Za-z0-9]{10,20}$")

_FUNGAL_PLAGUES = {"mildiu", "oídio", "oidio", "botritis", "fusarium"}
_INSECT_PLAGUES = {
    "tuta absoluta",
    "trips",
    "mosca blanca",
    "pulgón",
    "arañuela roja",
    "minador",
    "piojo harinoso",
    "oruga",
}


def user_has_siex_access(user: User) -> bool:
    if user.has_siex_module or user.has_siex_enterprise:
        return True
    if user.role in {"tech", "admin"}:
        return True
    return SIEX_PREVIEW_OPEN


def normalize_sigpac(code: str) -> str:
    return re.sub(r"\s+", "", code.strip().upper())


def validate_sigpac(code: str) -> str:
    normalized = normalize_sigpac(code)
    if not _SIGPAC_RE.match(normalized):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código SIGPAC inválido (10-20 caracteres alfanuméricos)",
        )
    return normalized


def _initial_status(user: User) -> str:
    if user.has_siex_enterprise:
        return "pendiente_validacion"
    return "registrado"


def _climate_snippet(db: Session, user: User, plague: str) -> str | None:
    if not climate_service.user_has_climate_access(user):
        return None
    try:
        alertas = climate_service.get_alertas(db)
    except Exception:
        return None

    plague_key = plague.strip().lower()
    lines: list[str] = []
    pool = (
        alertas.get("alertas_prioritarias")
        or alertas.get("alertas_combinadas")
        or alertas.get("alertas_reales")
        or []
    )
    for line in pool[:5]:
        low = line.lower()
        if plague_key in _FUNGAL_PLAGUES and any(k in low for k in ("humedad", "mildiu", "oídio", "oidio", "botritis", "riesgo", "estrés")):
            lines.append(line)
        elif plague_key in _INSECT_PLAGUES and any(k in low for k in ("estrés", "temperatura", "ventil", "dpv")):
            lines.append(line)
        elif not lines:
            lines.append(line)

    riesgo = alertas.get("riesgo_acumulado") or {}
    score = riesgo.get("score_pct") if isinstance(riesgo, dict) else None
    if score is not None:
        lines.append(f"Score de riesgo climático acumulado (7 d): {score}%.")

    if not lines:
        return None
    return "Contexto NEXO Climate:\n" + "\n".join(f"• {l}" for l in lines[:4])


def _build_texts(
    *,
    plague: str,
    crop: str,
    sigpac: str,
    product_name: str,
    registry_number: str | None,
    dose_ml: float | None,
    surface_m2: float | None,
    safety_hours: int,
    scan: Scan | None,
    climate_context: str | None,
    verified: bool = True,
) -> tuple[str, str]:
    reg = registry_number or "sin nº registro"
    dose_txt = f"{dose_ml} ml" if dose_ml is not None else "dosis no calculada"
    surface_txt = f"{surface_m2} m²" if surface_m2 is not None else "superficie no indicada"
    carencia_d = max(round(safety_hours / 24, 1), 0.1)

    que = (
        f"Aplicación fitosanitaria: {product_name} (MAPA {reg}) sobre {crop} "
        f"en recinto SIGPAC {sigpac}. Dosis aplicada: {dose_txt}. "
        f"Superficie tratada: {surface_txt}. Plazo de seguridad: {carencia_d} días."
    )

    detection = "diagnóstico en campo"
    if scan is not None:
        detection = f"escaneo PlagaScan (confianza {round(scan.confidence * 100)}%)"
        if verified and scan.corrected_plague:
            detection += f", validado por perito como «{scan.corrected_plague}»"
        elif verified:
            detection += ", confirmado por perito"
        else:
            detection += " — diagnóstico NO validado por perito (responsabilidad del agricultor)"

    justificacion = (
        f"Actuación fitosanitaria registrada tras detección de «{plague}» en cultivo «{crop}» "
        f"mediante {detection}. Producto seleccionado del vademécum MAPA autorizado para el binomio "
        f"plaga/cultivo. Tratamiento orientado a controlar la plaga detectada conforme a la ficha "
        f"oficial del producto."
    )
    if not verified:
        justificacion += (
            "\n\nAdvertencia: el tratamiento se registró sobre una plaga detectada por IA sin "
            "validación previa del perito técnico."
        )
    if climate_context:
        justificacion += f"\n\n{climate_context}"

    return que, justificacion


def _entry_read(db: Session, row: SiexCuadernoEntry) -> SiexEntryRead:
    farmer = db.query(User).filter(User.id == row.user_id).first()
    data = SiexEntryRead.model_validate(row)
    if farmer:
        data.farmer_name = farmer.name
        data.farmer_email = farmer.email
    return data


def compile_from_treatment(db: Session, user: User, treatment: FarmTreatment) -> SiexCuadernoEntry | None:
    if not user_has_siex_access(user):
        return None

    existing = (
        db.query(SiexCuadernoEntry).filter(SiexCuadernoEntry.treatment_id == treatment.id).first()
    )
    if existing:
        return existing

    farm: Farm | None = None
    if treatment.farm_id:
        farm = db.query(Farm).filter(Farm.id == treatment.farm_id, Farm.user_id == user.id).first()

    scan: Scan | None = None
    if treatment.scan_id:
        scan = db.query(Scan).filter(Scan.id == treatment.scan_id).first()

    if farm is None or not farm.sigpac_code:
        return None

    verified = is_scan_verified(scan)
    if scan and not verified and user.has_siex_enterprise:
        return None

    sigpac = validate_sigpac(farm.sigpac_code)
    zone_name = None
    if farm.zone_id:
        zone = db.query(AgriZone).filter(AgriZone.id == farm.zone_id).first()
        zone_name = zone.name if zone else None

    plague = effective_plague(scan, "plaga no indicada")
    crop = scan.crop if scan else farm.crop

    climate_context = _climate_snippet(db, user, plague)
    que, justificacion = _build_texts(
        plague=plague,
        crop=crop,
        sigpac=sigpac,
        product_name=treatment.product_name,
        registry_number=treatment.registry_number,
        dose_ml=treatment.dose_ml,
        surface_m2=farm.surface_m2,
        safety_hours=treatment.safety_hours,
        scan=scan,
        climate_context=climate_context,
        verified=verified,
    )

    row = SiexCuadernoEntry(
        user_id=user.id,
        farm_id=farm.id,
        treatment_id=treatment.id,
        scan_id=treatment.scan_id,
        sigpac_code=sigpac,
        farm_name=farm.name,
        zone_name=zone_name,
        crop=crop,
        plague=plague,
        product_name=treatment.product_name,
        registry_number=treatment.registry_number,
        active_substance=treatment.active_substance,
        dose_ml=treatment.dose_ml,
        surface_m2=farm.surface_m2,
        safety_hours=treatment.safety_hours,
        applied_at=treatment.applied_at,
        que_se_hizo=que,
        justificacion=justificacion,
        climate_context=climate_context,
        status=_initial_status(user),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_my_entries(db: Session, user_id: int) -> list[SiexEntryRead]:
    rows = (
        db.query(SiexCuadernoEntry)
        .filter(SiexCuadernoEntry.user_id == user_id)
        .order_by(SiexCuadernoEntry.applied_at.desc())
        .all()
    )
    return [_entry_read(db, r) for r in rows]


def list_pending_for_tech(db: Session) -> list[SiexEntryRead]:
    rows = (
        db.query(SiexCuadernoEntry)
        .filter(SiexCuadernoEntry.status == "pendiente_validacion")
        .order_by(SiexCuadernoEntry.created_at.asc())
        .all()
    )
    return [_entry_read(db, r) for r in rows]


def validate_entry(db: Session, entry_id: int, tech: User, payload: SiexEntryValidate) -> SiexEntryRead:
    row = db.query(SiexCuadernoEntry).filter(SiexCuadernoEntry.id == entry_id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrada SIEX no encontrada")
    if row.status not in {"pendiente_validacion", "registrado"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Entrada ya revisada")

    if payload.action == "approve":
        row.status = "validado"
    else:
        row.status = "rechazado"
    row.tech_notes = payload.tech_notes
    row.validated_by_id = tech.id
    row.validated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return _entry_read(db, row)


def export_validated(db: Session, user: User) -> dict:
    query = db.query(SiexCuadernoEntry).filter(SiexCuadernoEntry.status == "validado")
    if user.role not in {"tech", "admin"}:
        query = query.filter(SiexCuadernoEntry.user_id == user.id)
    rows = query.order_by(SiexCuadernoEntry.applied_at.desc()).all()
    entries = []
    for r in rows:
        entries.append(
            {
                "id": r.id,
                "sigpac": r.sigpac_code,
                "tipo": r.tipo_actuacion,
                "fecha": r.applied_at.isoformat(),
                "cultivo": r.crop,
                "plaga": r.plague,
                "producto": r.product_name,
                "registro_mapa": r.registry_number,
                "dosis_ml": r.dose_ml,
                "superficie_m2": r.surface_m2,
                "plazo_seguridad_horas": r.safety_hours,
                "que_se_hizo": r.que_se_hizo,
                "justificacion": r.justificacion,
            }
        )
    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "count": len(entries),
        "entries": entries,
    }
