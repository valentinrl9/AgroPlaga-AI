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
from app.models.pest_incident import PestIncident
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


def _resolve_farm(db: Session, user: User, treatment: FarmTreatment, scan: Scan | None) -> Farm | None:
    if treatment.farm_id is not None:
        farm = db.query(Farm).filter(Farm.id == treatment.farm_id, Farm.user_id == user.id).first()
        if farm is not None:
            return farm
    if scan is not None and scan.farm_id is not None:
        return db.query(Farm).filter(Farm.id == scan.farm_id, Farm.user_id == user.id).first()
    return None


def _resolve_incident(db: Session, treatment: FarmTreatment, scan: Scan | None) -> PestIncident | None:
    if treatment.scan_id is not None:
        incident = db.query(PestIncident).filter(PestIncident.scan_id == treatment.scan_id).first()
        if incident is not None:
            return incident
    return db.query(PestIncident).filter(PestIncident.treatment_id == treatment.id).first()


def _resolve_sigpac_for_entry(farm: Farm) -> tuple[str, str, bool]:
    """Devuelve (código SIGPAC, nota extra, ¿recinto real?)."""
    if farm.sigpac_code:
        return validate_sigpac(farm.sigpac_code), "", True
    placeholder = f"PEND{farm.id:06d}"
    note = (
        f"\n\nNota: falta el código SIGPAC del recinto invernadero en «{farm.name}». "
        "Añádelo en «Mis fincas» para completar el cuaderno con validez normativa plena."
    )
    return placeholder, note, False


def _entry_status(user: User, *, has_parcel_sigpac: bool) -> str:
    if not has_parcel_sigpac:
        return "pendiente_sigpac"
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

    scan: Scan | None = None
    if treatment.scan_id:
        scan = db.query(Scan).filter(Scan.id == treatment.scan_id).first()

    farm = _resolve_farm(db, user, treatment, scan)
    if farm is None:
        return None

    incident = _resolve_incident(db, treatment, scan)

    verified = is_scan_verified(scan)
    if scan and not verified and user.has_siex_enterprise:
        return None

    sigpac, sigpac_note, has_parcel_sigpac = _resolve_sigpac_for_entry(farm)
    zone_name = None
    if farm.zone_id:
        zone = db.query(AgriZone).filter(AgriZone.id == farm.zone_id).first()
        zone_name = zone.name if zone else None

    plague = incident.plague if incident else effective_plague(scan, "plaga no indicada")
    crop = incident.crop if incident else (scan.crop if scan else farm.crop)
    surface_m2 = (
        incident.prescription_surface_m2
        if incident and incident.prescription_surface_m2 is not None
        else farm.surface_m2
    )

    climate_context = _climate_snippet(db, user, plague)
    que, justificacion = _build_texts(
        plague=plague,
        crop=crop,
        sigpac=sigpac,
        product_name=treatment.product_name,
        registry_number=treatment.registry_number,
        dose_ml=treatment.dose_ml,
        surface_m2=surface_m2,
        safety_hours=treatment.safety_hours,
        scan=scan,
        climate_context=climate_context,
        verified=verified,
    )
    if sigpac_note:
        justificacion += sigpac_note

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
        surface_m2=surface_m2,
        safety_hours=treatment.safety_hours,
        applied_at=treatment.applied_at,
        que_se_hizo=que,
        justificacion=justificacion,
        climate_context=climate_context,
        status=_entry_status(user, has_parcel_sigpac=has_parcel_sigpac),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _refresh_entry_from_farm(db: Session, user: User, entry: SiexCuadernoEntry) -> bool:
    """Actualiza una entrada pendiente_sigpac cuando la finca ya tiene recinto SIGPAC."""
    if entry.status != "pendiente_sigpac":
        return False

    farm: Farm | None = None
    if entry.farm_id is not None:
        farm = db.query(Farm).filter(Farm.id == entry.farm_id, Farm.user_id == user.id).first()
    if farm is None or not farm.sigpac_code:
        return False

    treatment = db.query(FarmTreatment).filter(FarmTreatment.id == entry.treatment_id).first()
    if treatment is None:
        return False

    scan: Scan | None = None
    if entry.scan_id is not None:
        scan = db.query(Scan).filter(Scan.id == entry.scan_id).first()
    incident = _resolve_incident(db, treatment, scan)

    sigpac, _, has_parcel_sigpac = _resolve_sigpac_for_entry(farm)
    if not has_parcel_sigpac:
        return False

    verified = is_scan_verified(scan)
    plague = incident.plague if incident else effective_plague(scan, entry.plague)
    crop = incident.crop if incident else (scan.crop if scan else farm.crop)
    surface_m2 = (
        incident.prescription_surface_m2
        if incident and incident.prescription_surface_m2 is not None
        else entry.surface_m2 or farm.surface_m2
    )
    climate_context = entry.climate_context or _climate_snippet(db, user, plague)
    que, justificacion = _build_texts(
        plague=plague,
        crop=crop,
        sigpac=sigpac,
        product_name=entry.product_name,
        registry_number=entry.registry_number,
        dose_ml=entry.dose_ml,
        surface_m2=surface_m2,
        safety_hours=entry.safety_hours,
        scan=scan,
        climate_context=climate_context,
        verified=verified,
    )

    entry.sigpac_code = sigpac
    entry.que_se_hizo = que
    entry.justificacion = justificacion
    entry.status = _entry_status(user, has_parcel_sigpac=True)
    entry.farm_name = farm.name
    if farm.zone_id:
        zone = db.query(AgriZone).filter(AgriZone.id == farm.zone_id).first()
        if zone is not None:
            entry.zone_name = zone.name
    return True


def refresh_siex_entries_for_farm(db: Session, user: User, farm_id: int) -> int:
    """Refresca entradas SIEX pendientes de SIGPAC vinculadas a una finca."""
    rows = (
        db.query(SiexCuadernoEntry)
        .filter(
            SiexCuadernoEntry.user_id == user.id,
            SiexCuadernoEntry.farm_id == farm_id,
            SiexCuadernoEntry.status == "pendiente_sigpac",
        )
        .all()
    )
    updated = 0
    for row in rows:
        if _refresh_entry_from_farm(db, user, row):
            updated += 1
    if updated:
        db.commit()
    return updated


def _refresh_pending_sigpac_entries(db: Session, user: User) -> None:
    rows = (
        db.query(SiexCuadernoEntry)
        .filter(
            SiexCuadernoEntry.user_id == user.id,
            SiexCuadernoEntry.status == "pendiente_sigpac",
        )
        .all()
    )
    updated = False
    for row in rows:
        if _refresh_entry_from_farm(db, user, row):
            updated = True
    if updated:
        db.commit()


def list_my_entries(db: Session, user_id: int) -> list[SiexEntryRead]:
    user = db.query(User).filter(User.id == user_id).first()
    if user is not None:
        _sync_missing_entries(db, user)
        _refresh_pending_sigpac_entries(db, user)
    rows = (
        db.query(SiexCuadernoEntry)
        .filter(SiexCuadernoEntry.user_id == user_id)
        .order_by(SiexCuadernoEntry.applied_at.desc())
        .all()
    )
    return [_entry_read(db, r) for r in rows]


def _sync_missing_entries(db: Session, user: User) -> None:
    if not user_has_siex_access(user):
        return
    treatments = (
        db.query(FarmTreatment)
        .filter(FarmTreatment.user_id == user.id)
        .order_by(FarmTreatment.applied_at.desc())
        .limit(100)
        .all()
    )
    for treatment in treatments:
        exists = (
            db.query(SiexCuadernoEntry)
            .filter(SiexCuadernoEntry.treatment_id == treatment.id)
            .first()
        )
        if exists is None:
            compile_from_treatment(db, user, treatment)


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
