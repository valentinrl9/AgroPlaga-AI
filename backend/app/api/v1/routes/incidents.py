from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user
from app.models.farm import Farm
from app.models.farm_treatment import FarmTreatment
from app.models.pest_incident import PestIncident
from app.models.user import User
from app.models.zone import AgriZone
from app.schemas.pest_incident import (
    IncidentAdvance,
    IncidentApplyTreatment,
    IncidentAttachEvaluation,
    IncidentClose,
    IncidentCreate,
    IncidentEvaluate,
    IncidentPrescribe,
    IncidentRead,
    IncidentTreatmentSummary,
)
from app.services.pest_incident_service import (
    advance_incident,
    apply_treatment_to_incident,
    attach_evaluation_scan,
    close_incident,
    create_incident_from_scan,
    evaluate_incident,
    prescribe_incident,
    start_evaluation,
)
from app.services import treatment_service

router = APIRouter()


def _incident_read(db: Session, incident: PestIncident) -> IncidentRead:
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

    return IncidentRead(
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
    )


def _get_user_incident(db: Session, user: User, incident_id: int) -> PestIncident:
    incident = (
        db.query(PestIncident)
        .filter(PestIncident.id == incident_id, PestIncident.user_id == user.id)
        .first()
    )
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidencia no encontrada")
    return incident


@router.get("", response_model=list[IncidentRead])
def list_incidents(
    active_only: bool = Query(default=True),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(PestIncident).filter(PestIncident.user_id == current_user.id)
    if active_only:
        query = query.filter(PestIncident.stage != "closed")
    rows = query.order_by(PestIncident.updated_at.desc()).limit(200).all()
    return [_incident_read(db, row) for row in rows]


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(
    incident_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    incident = _get_user_incident(db, current_user, incident_id)
    return _incident_read(db, incident)


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def open_incident(
    body: IncidentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        incident = create_incident_from_scan(db, current_user, body.scan_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _incident_read(db, incident)


@router.patch("/{incident_id}/advance", response_model=IncidentRead)
def advance_incident_stage(
    incident_id: int,
    body: IncidentAdvance,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    incident = _get_user_incident(db, current_user, incident_id)
    try:
        incident = advance_incident(db, incident, body)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _incident_read(db, incident)


@router.patch("/{incident_id}/prescribe", response_model=IncidentRead)
def prescribe_incident_stage(
    incident_id: int,
    body: IncidentPrescribe,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    incident = _get_user_incident(db, current_user, incident_id)
    try:
        incident = prescribe_incident(db, current_user, incident, body)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _incident_read(db, incident)


@router.patch("/{incident_id}/apply-treatment", response_model=IncidentRead)
def apply_treatment_stage(
    incident_id: int,
    body: IncidentApplyTreatment,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    incident = _get_user_incident(db, current_user, incident_id)
    try:
        incident = apply_treatment_to_incident(db, current_user, incident, body)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _incident_read(db, incident)


@router.patch("/{incident_id}/start-evaluation", response_model=IncidentRead)
def start_evaluation_stage(
    incident_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    incident = _get_user_incident(db, current_user, incident_id)
    try:
        incident = start_evaluation(db, incident)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _incident_read(db, incident)


@router.patch("/{incident_id}/evaluation-scan", response_model=IncidentRead)
def attach_evaluation_scan_stage(
    incident_id: int,
    body: IncidentAttachEvaluation,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    incident = _get_user_incident(db, current_user, incident_id)
    try:
        incident = attach_evaluation_scan(db, current_user, incident, body)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _incident_read(db, incident)


@router.patch("/{incident_id}/evaluate", response_model=IncidentRead)
def evaluate_incident_stage(
    incident_id: int,
    body: IncidentEvaluate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    incident = _get_user_incident(db, current_user, incident_id)
    try:
        incident = evaluate_incident(db, incident, body)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _incident_read(db, incident)


@router.patch("/{incident_id}/close", response_model=IncidentRead)
def close_incident_stage(
    incident_id: int,
    body: IncidentClose,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    incident = _get_user_incident(db, current_user, incident_id)
    try:
        incident = close_incident(db, incident, body)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _incident_read(db, incident)
