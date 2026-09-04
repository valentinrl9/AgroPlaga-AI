from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.farm_treatment import FarmTreatment
from app.models.outbreak_event import OutbreakEvent
from app.models.pest_incident import CLOSURE_OUTCOMES, PestIncident
from app.models.scan import Scan
from app.models.user import User
from app.schemas.outbreak_event import OutbreakEventCreate
from app.models.zone import AgriZone
from app.schemas.pest_incident import (
    IncidentAdvance,
    IncidentApplyTreatment,
    IncidentAttachEvaluation,
    IncidentClose,
    IncidentEvaluate,
    IncidentPrescribe,
    IncidentTreatmentSummary,
    TechIncidentRead,
)
from app.schemas.treatment import DoseCalculateRequest, TreatmentCreate, TreatmentRead
from app.services.outbreak_event_service import create_anonymous_event
from app.services.recommendation_service import _severity_level
from app.services import treatment_service
from app.services.scan_validation import effective_plague
from app.services.user_consent_service import ensure_map_consent
from app.data.plague_catalog import normalize_plague


def _now() -> datetime:
    return datetime.now(timezone.utc)


def is_trackable_plague(plague: str) -> bool:
    return normalize_plague(plague) != "sana"


def _resolve_zone_id(db: Session, scan: Scan) -> int:
    if scan.farm_id is None:
        raise ValueError("Vincula el escaneo a una finca con municipio antes de abrir incidencia")
    farm = db.query(Farm).filter(Farm.id == scan.farm_id).first()
    if farm is None or farm.zone_id is None:
        raise ValueError("La finca del escaneo debe tener municipio asignado")
    return farm.zone_id


def create_incident_from_scan(db: Session, user: User, scan_id: int) -> PestIncident:
    ensure_map_consent(db, user)

    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == user.id).first()
    if scan is None:
        raise ValueError("Escaneo no encontrado")

    plague = effective_plague(scan)
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
    product = treatment_service.get_biocide_product(
        db,
        payload.registry_no,
        incident.plague,
        incident.crop,
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
    incident.prescription_surface_m2 = payload.surface_m2
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
) -> tuple[PestIncident, TreatmentRead]:
    if incident.stage != "prescription":
        raise ValueError("Registra la prescripción antes de aplicar tratamiento")
    if not incident.prescription_product_name or incident.prescription_safety_hours is None:
        raise ValueError("Falta prescripción MAPA en la incidencia")

    scan = db.query(Scan).filter(Scan.id == incident.scan_id).first()
    farm_id = incident.farm_id or (scan.farm_id if scan else None)

    treatment = treatment_service.create_treatment(
        db,
        user,
        TreatmentCreate(
            farm_id=farm_id,
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
    if incident.farm_id is None and farm_id is not None:
        incident.farm_id = farm_id
    incident.stage = "treatment"
    incident.updated_at = _now()
    db.add(incident)
    db.commit()
    db.refresh(incident)

    from app.services.user_notification_service import create_user_notification

    product = incident.prescription_product_name or "tratamiento"
    create_user_notification(
        db,
        user_id=user.id,
        notification_type="incident_carencia",
        title="Tratamiento registrado",
        body=f"{product} · respeta la carencia antes de recolectar.",
        section="incidents",
        reference_type="incident",
        reference_id=incident.id,
        dedupe_key=f"treatment_applied:{incident.id}",
        skip_dedupe=True,
    )
    return incident, treatment


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


def _incident_to_tech_read(db: Session, incident: PestIncident, farmer: User) -> TechIncidentRead:
    zone = db.query(AgriZone).filter(AgriZone.id == incident.zone_id).first()
    farm_name = None
    farm_surface_m2 = None
    if incident.farm_id is not None:
        farm = db.query(Farm).filter(Farm.id == incident.farm_id).first()
        if farm is not None:
            farm_name = farm.name
            farm_surface_m2 = farm.surface_m2

    treatment_summary: IncidentTreatmentSummary | None = None
    if incident.treatment_id is not None:
        row = db.query(FarmTreatment).filter(FarmTreatment.id == incident.treatment_id).first()
        if row is not None:
            read = treatment_service._treatment_read(row)
            treatment_summary = IncidentTreatmentSummary(
                id=read.id,
                product_name=read.product_name,
                safety_hours=read.safety_hours,
                hours_remaining=read.hours_remaining,
                harvest_allowed=read.harvest_allowed,
            )

    return TechIncidentRead(
        id=incident.id,
        scan_id=incident.scan_id,
        farm_id=incident.farm_id,
        farm_name=farm_name,
        zone_id=incident.zone_id,
        zone_name=zone.name if zone else None,
        outbreak_event_id=incident.outbreak_event_id,
        plague=incident.plague,
        crop=incident.crop,
        severity=incident.severity,
        stage=incident.stage,
        closure_outcome=incident.closure_outcome,
        notes=incident.notes,
        prescription_product_name=incident.prescription_product_name,
        prescription_registry_number=incident.prescription_registry_number,
        prescription_dose_ml=incident.prescription_dose_ml,
        prescription_safety_hours=incident.prescription_safety_hours,
        prescription_surface_m2=incident.prescription_surface_m2,
        prescription_active_substance=incident.prescription_active_substance,
        farm_surface_m2=farm_surface_m2,
        treatment=treatment_summary,
        evaluation_scan_id=incident.evaluation_scan_id,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        closed_at=incident.closed_at,
        farmer_name=farmer.name,
        farmer_email=farmer.email,
    )


def list_incidents_for_tech(db: Session, *, active_only: bool = True) -> list[TechIncidentRead]:
    query = db.query(PestIncident, User).join(User, PestIncident.user_id == User.id)
    if active_only:
        query = query.filter(PestIncident.stage != "closed")
    rows = query.order_by(PestIncident.updated_at.desc()).limit(200).all()
    return [_incident_to_tech_read(db, incident, farmer) for incident, farmer in rows]
