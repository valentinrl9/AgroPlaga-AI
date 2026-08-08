from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.biocide_product import BiocideProduct
from app.models.farm import Farm
from app.models.farm_treatment import FarmTreatment
from app.models.outbreak_event import OutbreakEvent
from app.models.pest_incident import CLOSURE_OUTCOMES, PestIncident
from app.models.scan import Scan
from app.models.user import User
from app.schemas.outbreak_event import OutbreakEventCreate
from app.schemas.pest_incident import (
    IncidentAdvance,
    IncidentApplyTreatment,
    IncidentAttachEvaluation,
    IncidentClose,
    IncidentEvaluate,
    IncidentPrescribe,
)
from app.schemas.treatment import DoseCalculateRequest, TreatmentCreate
from app.services.outbreak_event_service import create_anonymous_event
from app.services.recommendation_service import _severity_level
from app.services import treatment_service
from app.data.plague_catalog import normalize_plague


def _now() -> datetime:
    return datetime.now(timezone.utc)


def is_trackable_plague(plague: str) -> bool:
    return normalize_plague(plague) != "sana"


def _effective_plague(scan: Scan) -> str:
    if scan.corrected_plague:
        return scan.corrected_plague.strip().lower()
    return scan.plague.strip().lower()


def _resolve_zone_id(db: Session, scan: Scan) -> int:
    if scan.farm_id is None:
        raise ValueError("Vincula el escaneo a una finca con municipio antes de abrir incidencia")
    farm = db.query(Farm).filter(Farm.id == scan.farm_id).first()
    if farm is None or farm.zone_id is None:
        raise ValueError("La finca del escaneo debe tener municipio asignado")
    return farm.zone_id


def create_incident_from_scan(db: Session, user: User, scan_id: int) -> PestIncident:
    if user.consent_accepted_at is None:
        raise ValueError("Se requiere consentimiento de mapa anónimo para abrir incidencias")

    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == user.id).first()
    if scan is None:
        raise ValueError("Escaneo no encontrado")

    plague = _effective_plague(scan)
    if not is_trackable_plague(plague):
        raise ValueError("Los escaneos sin plaga relevante no generan incidencia")

    existing = db.query(PestIncident).filter(PestIncident.scan_id == scan.id).first()
    if existing is not None:
        raise ValueError("Ya existe una incidencia para este escaneo")

    zone_id = _resolve_zone_id(db, scan)
    event = create_anonymous_event(
        db,
        OutbreakEventCreate(
            plague=plague,
            severity=_severity_level(scan.severity),
            zone_id=zone_id,
            model_version="v2.0",
            source_scan_id=scan.id,
        ),
        contributor_id=user.id,
    )
    event.status = "active"
    db.add(event)
    db.flush()

    now = _now()
    incident = PestIncident(
        user_id=user.id,
        scan_id=scan.id,
        farm_id=scan.farm_id,
        zone_id=zone_id,
        outbreak_event_id=event.id,
        plague=plague,
        crop=scan.crop.strip(),
        severity=_severity_level(scan.severity),
        stage="detection",
        created_at=now,
        updated_at=now,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def advance_incident(db: Session, incident: PestIncident, payload: IncidentAdvance) -> PestIncident:
    if incident.stage == "closed":
        raise ValueError("La incidencia ya está cerrada")
    if incident.stage != "detection":
        raise ValueError("Solo puedes avanzar de Detección a Diagnóstico desde aquí")

    incident.stage = "diagnosis"
    incident.updated_at = _now()
    if payload.notes:
        incident.notes = payload.notes.strip()
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def prescribe_incident(db: Session, user: User, incident: PestIncident, payload: IncidentPrescribe) -> PestIncident:
    if incident.stage not in {"diagnosis", "prescription"}:
        raise ValueError("La prescripción solo está disponible en diagnóstico o prescripción")

    crop_key = incident.crop.strip().lower()
    product = (
        db.query(BiocideProduct)
        .filter(
            BiocideProduct.registry_no == payload.registry_no.strip(),
            BiocideProduct.plague == incident.plague,
            BiocideProduct.crop == crop_key,
        )
        .first()
    )
    if product is None:
        raise ValueError("Producto MAPA no encontrado para esta plaga y cultivo")

    dose = treatment_service.calculate_dose(
        db,
        DoseCalculateRequest(
            registry_no=payload.registry_no.strip(),
            surface_m2=payload.surface_m2,
            plague=incident.plague,
            crop=crop_key,
        ),
    )

    incident.prescription_product_name = product.name
    incident.prescription_registry_number = product.registry_no
    incident.prescription_active_substance = product.active_substance
    incident.prescription_dose_ml = dose.dose_ml
    incident.prescription_safety_hours = dose.safety_hours
    incident.stage = "prescription"
    incident.updated_at = _now()
    if payload.notes:
        incident.notes = payload.notes.strip()
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def apply_treatment_to_incident(
    db: Session,
    user: User,
    incident: PestIncident,
    payload: IncidentApplyTreatment,
) -> PestIncident:
    if incident.stage != "prescription":
        raise ValueError("Registra la prescripción antes de aplicar tratamiento")
    if not incident.prescription_product_name or incident.prescription_safety_hours is None:
        raise ValueError("Falta prescripción MAPA en la incidencia")

    treatment = treatment_service.create_treatment(
        db,
        user,
        TreatmentCreate(
            farm_id=incident.farm_id,
            scan_id=incident.scan_id,
            product_name=incident.prescription_product_name,
            registry_number=incident.prescription_registry_number,
            active_substance=incident.prescription_active_substance,
            safety_hours=incident.prescription_safety_hours,
            dose_ml=incident.prescription_dose_ml,
            notes=payload.notes,
            ack_unverified=payload.ack_unverified,
        ),
    )

    row = db.query(FarmTreatment).filter(FarmTreatment.id == treatment.id).first()
    incident.treatment_id = row.id if row else treatment.id
    incident.stage = "treatment"
    incident.updated_at = _now()
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def start_evaluation(db: Session, incident: PestIncident) -> PestIncident:
    if incident.stage != "treatment":
        raise ValueError("Solo puedes evaluar tras registrar el tratamiento")
    if incident.treatment_id is None:
        raise ValueError("Falta tratamiento registrado")

    incident.stage = "evaluation"
    incident.updated_at = _now()
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def attach_evaluation_scan(
    db: Session,
    user: User,
    incident: PestIncident,
    payload: IncidentAttachEvaluation,
) -> PestIncident:
    if incident.stage != "evaluation":
        raise ValueError("Solo puedes adjuntar foto comparativa en evaluación")

    scan = db.query(Scan).filter(
        Scan.id == payload.evaluation_scan_id,
        Scan.user_id == user.id,
    ).first()
    if scan is None:
        raise ValueError("Escaneo de evaluación no encontrado")

    incident.evaluation_scan_id = scan.id
    incident.updated_at = _now()
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def evaluate_incident(db: Session, incident: PestIncident, payload: IncidentEvaluate) -> PestIncident:
    if incident.stage != "evaluation":
        raise ValueError("Solo puedes evaluar incidencias en etapa de evaluación")

    incident.updated_at = _now()
    if payload.notes:
        incident.notes = payload.notes.strip()
    if payload.evaluation_scan_id is not None:
        incident.evaluation_scan_id = payload.evaluation_scan_id

    if payload.improved:
        incident.stage = "closed"
        incident.closure_outcome = "resolved"
        incident.closed_at = _now()
        _close_outbreak_event(db, incident)
    else:
        incident.stage = "treatment"

    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def close_incident(db: Session, incident: PestIncident, payload: IncidentClose) -> PestIncident:
    if incident.stage == "closed":
        raise ValueError("La incidencia ya está cerrada")
    if payload.outcome not in CLOSURE_OUTCOMES:
        raise ValueError("Resultado de cierre no válido")

    incident.stage = "closed"
    incident.closure_outcome = payload.outcome
    incident.closed_at = _now()
    incident.updated_at = _now()
    if payload.notes:
        incident.notes = payload.notes.strip()

    _close_outbreak_event(db, incident)
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def _close_outbreak_event(db: Session, incident: PestIncident) -> None:
    if incident.outbreak_event_id is None:
        return
    event = db.query(OutbreakEvent).filter(OutbreakEvent.id == incident.outbreak_event_id).first()
    if event is None:
        return
    event.status = "closed"
    db.add(event)


def stage_label(stage: str) -> str:
    labels = {
        "detection": "Detección",
        "diagnosis": "Diagnóstico",
        "prescription": "Prescripción",
        "treatment": "Tratamiento",
        "evaluation": "Evaluación",
        "closed": "Cierre",
    }
    return labels.get(stage, stage)
