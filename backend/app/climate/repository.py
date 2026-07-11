"""Persistencia PostgreSQL para agregados climáticos."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models.climate import ClimateDaily, ClimateMonthly, ClimateWeekly


def _clean(value):
    if value is None:
        return None
    if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
        return None
    if pd.isna(value):
        return None
    return value


def _load_daily(db: Session, df: pd.DataFrame) -> None:
    if df.empty:
        return
    db.query(ClimateDaily).delete()
    for row in df.itertuples(index=False):
        db.add(
            ClimateDaily(
                fecha=row.fecha,
                et0_diaria=_clean(row.et0_diaria),
                radiacion_diaria=_clean(row.radiacion_diaria),
                temperatura_media=_clean(row.temperatura_media),
                humedad_media=_clean(row.humedad_media),
                viento_medio=_clean(row.viento_medio),
                precipitacion_diaria=_clean(row.precipitacion_diaria),
                estres_termico_medio=_clean(row.estres_termico_medio),
            )
        )


def _load_weekly(db: Session, df: pd.DataFrame) -> None:
    if df.empty:
        return
    db.query(ClimateWeekly).delete()
    for row in df.itertuples(index=False):
        db.add(
            ClimateWeekly(
                semana_id=row.semana_id,
                et0_semanal=_clean(row.et0_semanal),
                radiacion_semanal=_clean(row.radiacion_semanal),
                temperatura_media_semanal=_clean(row.temperatura_media_semanal),
                humedad_media_semanal=_clean(row.humedad_media_semanal),
                viento_medio_semanal=_clean(row.viento_medio_semanal),
                precipitacion_semanal=_clean(row.precipitacion_semanal),
                estres_termico_semanal=_clean(row.estres_termico_semanal),
            )
        )


def _load_monthly(db: Session, df: pd.DataFrame) -> None:
    if df.empty:
        return
    db.query(ClimateMonthly).delete()
    for row in df.itertuples(index=False):
        db.add(
            ClimateMonthly(
                mes=row.mes,
                et0_mensual=_clean(row.et0_mensual),
                radiacion_mensual=_clean(row.radiacion_mensual),
                temperatura_media_mes=_clean(row.temperatura_media_mes),
                humedad_media_mes=_clean(row.humedad_media_mes),
                viento_medio_mes=_clean(row.viento_medio_mes),
                precipitacion_mensual=_clean(row.precipitacion_mensual),
                estres_termico_mes=_clean(row.estres_termico_mes),
            )
        )


def load_aggregates(db: Session, diario: pd.DataFrame, semanal: pd.DataFrame, mensual: pd.DataFrame) -> None:
    _load_daily(db, diario)
    _load_weekly(db, semanal)
    _load_monthly(db, mensual)
    db.commit()


def count_daily(db: Session) -> int:
    return db.query(ClimateDaily).count()


def get_last_n_daily(db: Session, n: int) -> list[dict]:
    rows = (
        db.query(ClimateDaily)
        .order_by(ClimateDaily.fecha.desc())
        .limit(n)
        .all()
    )
    rows = list(reversed(rows))
    return [_daily_to_dict(r) for r in rows]


def get_daily_between(db: Session, start, end) -> list[dict]:
    rows = (
        db.query(ClimateDaily)
        .filter(ClimateDaily.fecha >= start, ClimateDaily.fecha <= end)
        .order_by(ClimateDaily.fecha.asc())
        .all()
    )
    return [_daily_to_dict(r) for r in rows]


def get_max_fecha(db: Session):
    row = db.query(ClimateDaily.fecha).order_by(ClimateDaily.fecha.desc()).first()
    return row[0] if row else None


def _daily_to_dict(row: ClimateDaily) -> dict:
    return {
        "fecha": row.fecha.isoformat() if hasattr(row.fecha, "isoformat") else str(row.fecha),
        "et0_diaria": row.et0_diaria,
        "radiacion_diaria": row.radiacion_diaria,
        "temperatura_media": row.temperatura_media,
        "humedad_media": row.humedad_media,
        "viento_medio": row.viento_medio,
        "precipitacion_diaria": row.precipitacion_diaria,
        "estres_termico_medio": row.estres_termico_medio,
    }
