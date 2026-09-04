"""Recordatorios programados: incidencias abiertas y vigilancia semanal."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.farm_treatment import FarmTreatment
from app.models.pest_incident import PestIncident
from app.models.user import User
from app.services.gamification_service import WEEKLY_SCAN_GOAL, _weekly_scans, get_weekly_vigilance
from app.services.pest_incident_service import stage_label
from app.services.treatment_service import _treatment_read
from app.services.user_notification_service import (
    create_user_notification,
    notify_carencia_done,
    notify_incident_reminder,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _hours_since(dt: datetime | None) -> float:
    if dt is None:
        return 0.0
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (_now() - dt).total_seconds() / 3600.0


def _incident_reminder_message(incident: PestIncident, treatment_read) -> tuple[str, str, str] | None:
    """Devuelve (title, body, reminder_kind) o None."""
    plague = incident.plague
    stage = incident.stage

    if stage == "detection" and _hours_since(incident.created_at) >= 24:
        return (
            f"Incidencia · {plague}",
            "Confirma el diagnóstico en la incidencia abierta.",
            "detection_stale",
        )
    if stage == "diagnosis" and _hours_since(incident.updated_at) >= 48:
        return (
            f"Incidencia · {plague}",
            "Completa la prescripción MAPA o consulta con tu técnico.",
            "diagnosis_stale",
        )
    if stage == "prescription":
        product = incident.prescription_product_name or "tratamiento"
        return (
            f"Pendiente tratamiento · {plague}",
            f"Aplica el producto prescrito: {product}.",
            "apply_treatment",
        )
    if stage == "treatment" and treatment_read is not None:
        if not treatment_read.harvest_allowed:
            hours = treatment_read.hours_remaining or 0
            return (
                "Recolección prohibida",
                f"{treatment_read.product_name} · {hours:.0f} h de carencia restantes.",
                "carencia_active",
            )
        if _hours_since(incident.updated_at) >= 24:
            return (
                f"Seguimiento · {plague}",
                "Carencia cumplida — haz una foto de seguimiento para comprobar si mejoró.",
                "evaluation_due",
            )
    if stage == "evaluation":
        if incident.evaluation_scan_id is None:
            return (
                f"Foto comparativa · {plague}",
                "Adjunta un escaneo en la misma zona para evaluar la evolución.",
                "eval_photo",
            )
        return (
            f"Valorar evolución · {plague}",
            "¿Ha mejorado la plaga? Confirma el resultado en la incidencia.",
            "eval_confirm",
        )
    return None


def run_incident_reminders(db: Session) -> int:
    """Recorre incidencias abiertas y crea recordatorios deduplicados."""
    rows = db.query(PestIncident).filter(PestIncident.stage != "closed").all()
    created = 0
    for incident in rows:
        treatment_read = None
        if incident.treatment_id is not None:
            row = db.query(FarmTreatment).filter(FarmTreatment.id == incident.treatment_id).first()
            if row is not None:
                treatment_read = _treatment_read(row)
                if treatment_read.harvest_allowed and incident.stage == "treatment":
                    if notify_carencia_done(
                        db,
                        user_id=incident.user_id,
                        incident_id=incident.id,
                        product_name=treatment_read.product_name,
                    ):
                        created += 1

        msg = _incident_reminder_message(incident, treatment_read)
        if msg is None:
            continue
        title, body, kind = msg
        if notify_incident_reminder(
            db,
            user_id=incident.user_id,
            incident_id=incident.id,
            title=title,
            body=body,
            reminder_kind=kind,
        ):
            created += 1
    return created


def run_weekly_vigilance_reminders(db: Session) -> int:
    """Recordatorio si el agricultor no completó el reto semanal (mar/jue)."""
    now = _now()
    if now.weekday() not in {1, 3}:  # martes y jueves UTC
        return 0

    farmers = db.query(User).filter(User.role == "farmer").all()
    created = 0
    year, week, _ = now.isocalendar()
    dedupe_suffix = f"{year}_W{week:02d}"

    for farmer in farmers:
        vigilance = get_weekly_vigilance(db, farmer)
        if vigilance["completed"]:
            continue
        dedupe_key = f"weekly_vigilance:{dedupe_suffix}"
        row = create_user_notification(
            db,
            user_id=farmer.id,
            notification_type="weekly_vigilance",
            title="Reto de la semana",
            body="Haz al menos 1 escaneo con PlagaScan (aunque la hoja esté sana). Llevas 0/1.",
            section="community",
            dedupe_key=dedupe_key,
        )
        if row is not None:
            created += 1
    return created


def count_open_incidents_needing_action(db: Session, user_id: int) -> int:
    rows = db.query(PestIncident).filter(
        PestIncident.user_id == user_id,
        PestIncident.stage != "closed",
    ).all()
    count = 0
    for incident in rows:
        treatment_read = None
        if incident.treatment_id is not None:
            row = db.query(FarmTreatment).filter(FarmTreatment.id == incident.treatment_id).first()
            if row is not None:
                treatment_read = _treatment_read(row)
        if _incident_reminder_message(incident, treatment_read) is not None:
            count += 1
        elif incident.stage in {"prescription", "evaluation"}:
            count += 1
        elif incident.stage == "detection":
            count += 1
    return count


def run_all_scheduled_reminders(db: Session) -> dict[str, int]:
    return {
        "incident_reminders": run_incident_reminders(db),
        "weekly_vigilance": run_weekly_vigilance_reminders(db),
    }
