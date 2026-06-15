from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user, require_roles
from app.models.alert import Alert
from app.models.alert_preference import UserAlertPreference
from app.models.outbreak_event import OutbreakEvent
from app.models.user import User
from app.models.zone import AgriZone
from app.schemas.alert import (
    AlertDismiss,
    AlertPreferenceItem,
    AlertPreferencesRead,
    AlertPreferencesUpdate,
    AlertRead,
)
from app.services.alert_engine import run_alert_scan
from app.services.heatmap_service import get_heatmap_grid

router = APIRouter()

TECH_OR_ADMIN = require_roles(["tech", "admin"])


def _available_plagues(db: Session) -> list[str]:
    rows = db.query(OutbreakEvent.plague).distinct().order_by(OutbreakEvent.plague).all()
    return [row[0] for row in rows]


def _user_enabled_plagues(db: Session, user_id: int) -> set[str] | None:
    prefs = db.query(UserAlertPreference).filter(UserAlertPreference.user_id == user_id).all()
    if not prefs:
        return None
    return {pref.plague for pref in prefs if pref.enabled}


def _alert_to_read(alert: Alert, zone_name: str | None) -> AlertRead:
    return AlertRead(
        id=alert.id,
        zone_id=alert.zone_id,
        zone_name=zone_name,
        plague=alert.plague,
        alert_type=alert.alert_type,
        description=alert.description,
        priority_score=alert.priority_score,
        created_at=alert.created_at,
        active=alert.active,
    )


@router.get("", response_model=list[AlertRead])
def list_alerts(
    zone_id: int | None = Query(default=None),
    plague: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(Alert, AgriZone.name).outerjoin(AgriZone, Alert.zone_id == AgriZone.id)
    if zone_id is not None:
        query = query.filter(Alert.zone_id == zone_id)
    if plague:
        query = query.filter(Alert.plague == plague.strip().lower())
    if active_only:
        query = query.filter(Alert.active.is_(True))

    enabled_plagues = _user_enabled_plagues(db, current_user.id)
    if enabled_plagues is not None:
        query = query.filter(Alert.plague.in_(enabled_plagues))

    rows = query.order_by(Alert.priority_score.desc().nullslast(), Alert.created_at.desc()).limit(100).all()
    return [_alert_to_read(alert, zone_name) for alert, zone_name in rows]


@router.get("/preferences", response_model=AlertPreferencesRead)
def get_alert_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    available = _available_plagues(db)
    prefs = (
        db.query(UserAlertPreference)
        .filter(UserAlertPreference.user_id == current_user.id)
        .order_by(UserAlertPreference.plague)
        .all()
    )
    pref_map = {pref.plague: pref.enabled for pref in prefs}
    preferences = [
        AlertPreferenceItem(plague=plague, enabled=pref_map.get(plague, True))
        for plague in available
    ]
    return AlertPreferencesRead(preferences=preferences, available_plagues=available)


@router.put("/preferences", response_model=AlertPreferencesRead)
def update_alert_preferences(
    body: AlertPreferencesUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    available = set(_available_plagues(db))
    for item in body.preferences:
        plague = item.plague.strip().lower()
        if plague not in available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Plaga desconocida: {plague}",
            )

    db.query(UserAlertPreference).filter(UserAlertPreference.user_id == current_user.id).delete()
    for item in body.preferences:
        db.add(
            UserAlertPreference(
                user_id=current_user.id,
                plague=item.plague.strip().lower(),
                enabled=item.enabled,
            )
        )
    db.commit()
    return get_alert_preferences(current_user=current_user, db=db)


@router.post("/scan", status_code=status.HTTP_202_ACCEPTED)
def trigger_alert_scan(
    _user: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    created = run_alert_scan(db)
    return {"created": created, "message": "Escaneo de alertas completado"}


@router.patch("/{alert_id}", response_model=AlertRead)
def update_alert(
    alert_id: int,
    body: AlertDismiss,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    row = (
        db.query(Alert, AgriZone.name)
        .outerjoin(AgriZone, Alert.zone_id == AgriZone.id)
        .filter(Alert.id == alert_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta no encontrada")

    alert, zone_name = row
    alert.active = body.active
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return _alert_to_read(alert, zone_name)


@router.get("/heatmap-preview")
def heatmap_preview(
    plague: str | None = Query(default=None),
    hours: int = Query(default=168, ge=1, le=720),
    min_severity: int = Query(default=1, ge=1, le=3),
    _current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return {
        "cells": get_heatmap_grid(
            db,
            plague=plague,
            hours=hours,
            min_severity=min_severity,
        )
    }
