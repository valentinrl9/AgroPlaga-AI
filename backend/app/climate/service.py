"""Lógica de negocio NEXO Climate (portado desde AgroData)."""

from __future__ import annotations

import json
from datetime import timedelta

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session

from app.climate.config import (
    CLIMATE_PREVIEW_OPEN,
    DATASET_FINAL_CSV,
    ETL_INTERVAL_SECONDS,
    ETL_LAST_RUN_JSON,
    LAT,
    LON,
    REALTIME_CSV,
)
from app.climate.metrics import calc_dew_point_c, calc_dpv_kpa, dpv_status
from app.climate.openmeteo_transform import calc_estres_termico
from app.climate.repository import get_daily_between, get_last_n_daily, get_max_fecha, count_daily
from app.models.user import User


def user_has_climate_access(user: User) -> bool:
    if user.has_climate_module:
        return True
    if user.role in ("tech", "admin"):
        return True
    return CLIMATE_PREVIEW_OPEN


def get_health(db: Session) -> dict:
    return {
        "status": "ok" if count_daily(db) > 0 else "degraded",
        "postgres": True,
        "climate_daily_rows": count_daily(db),
        "realtime_csv": REALTIME_CSV.exists(),
        "ubicacion": {"lat": LAT, "lon": LON},
        "preview_open": CLIMATE_PREVIEW_OPEN,
    }


def get_etl_status() -> dict:
    if not ETL_LAST_RUN_JSON.exists():
        return {
            "success": None,
            "last_run": None,
            "interval_seconds": ETL_INTERVAL_SECONDS,
            "interval_minutes": ETL_INTERVAL_SECONDS // 60,
        }
    try:
        data = json.loads(ETL_LAST_RUN_JSON.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"success": False, "error": "No se pudo leer etl_last_run.json"}
    finished = data.get("finished_at")
    return {
        **data,
        "last_run": finished,
        "interval_seconds": ETL_INTERVAL_SECONDS,
        "interval_minutes": ETL_INTERVAL_SECONDS // 60,
    }


def _metricas_dia(ts) -> dict | None:
    hoy = pd.to_datetime(ts).date()
    if not DATASET_FINAL_CSV.exists():
        return None
    df = pd.read_csv(DATASET_FINAL_CSV)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df[df["timestamp"].dt.date == hoy].sort_values("timestamp")
    if df.empty:
        return None
    df = df.copy()
    df["hora"] = df["timestamp"].dt.floor("h")
    df = df.drop_duplicates(subset=["hora"], keep="last")
    df["estres"] = calc_estres_termico(df)
    et0_series = df["et0_fao_evapotranspiration"].astype(float)
    if et0_series.max() > 2.0:
        et0_dia = float(et0_series.iloc[-1])
        et0_parcial = True
    else:
        et0_dia = float(et0_series.sum())
        et0_parcial = len(df) < 20
    return {
        "et0_dia": round(et0_dia, 2),
        "estres_termico": round(float(df["estres"].mean()), 2),
        "humedad_media": round(float(df["relative_humidity_2m"].mean()), 1),
        "et0_parcial": et0_parcial,
    }


def get_actual(db: Session) -> dict:
    del db
    try:
        df = pd.read_csv(REALTIME_CSV)
    except Exception as exc:
        return {"error": f"No se pudo leer realtime: {exc}"}
    if df.empty:
        return {"error": "Realtime vacío. Ejecuta ETL primero."}

    row = df.iloc[-1]
    ts = row["timestamp"]
    t = float(row["temperature_2m"])
    rh = float(row["relative_humidity_2m"])
    dpv = calc_dpv_kpa(t, rh)

    salida = {
        "timestamp": str(ts),
        "et0_hora": round(float(row["et0_fao_evapotranspiration"]), 2),
        "temperatura": t,
        "humedad": rh,
        "radiacion": float(row["shortwave_radiation"]),
        "viento": float(row["wind_speed_10m"]),
        "precipitacion": float(row["precipitation"]),
        "dpv_kpa": round(dpv, 3),
        "dpv_status": dpv_status(dpv),
        "punto_rocio_c": round(calc_dew_point_c(t, rh), 2),
        "estres_instantaneo": round(
            float(
                calc_estres_termico(
                    pd.DataFrame(
                        [{
                            "temperature_2m": t,
                            "shortwave_radiation": row["shortwave_radiation"],
                            "wind_speed_10m": row["wind_speed_10m"],
                        }]
                    )
                ).iloc[0]
            ),
            2,
        ),
    }
    metricas = _metricas_dia(ts)
    if metricas:
        salida.update(metricas)
    else:
        salida["et0_dia"] = salida.get("et0_hora", 0)
        salida["estres_termico"] = salida["estres_instantaneo"]
        salida["humedad_media"] = rh
        salida["et0_parcial"] = True
    return salida


def get_prediccion(db: Session, dias: int = 7) -> list[dict] | dict:
    rows = get_last_n_daily(db, 14)
    if not rows:
        return {"error": "No hay datos en climate_daily. Ejecuta ETL."}

    df = pd.DataFrame(rows)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha")
    df["t"] = (df["fecha"] - df["fecha"].min()).dt.days

    variables = [
        "et0_diaria",
        "radiacion_diaria",
        "temperatura_media",
        "humedad_media",
        "viento_medio",
        "precipitacion_diaria",
        "estres_termico_medio",
    ]
    modelos = {}
    for var in variables:
        y = df[var].values
        x = df["t"].values.reshape(-1, 1)
        lr = LinearRegression().fit(x, y)
        rf = RandomForestRegressor(n_estimators=200, random_state=42).fit(x, y)
        modelos[var] = (lr, rf)

    hoy = df["fecha"].max().date()
    ultimo_t = int(df["t"].max())
    predicciones = []
    for i in range(1, dias + 1):
        t_futuro = ultimo_t + i
        fecha_futura = hoy + timedelta(days=i)
        pred = {"fecha": fecha_futura.isoformat()}
        for var in variables:
            lr, rf = modelos[var]
            pred_lr = lr.predict(np.array([[t_futuro]]))[0]
            pred_rf = rf.predict(np.array([[t_futuro]]))[0]
            valor = (pred_lr + pred_rf) / 2
            if var in ["et0_diaria", "radiacion_diaria", "precipitacion_diaria"]:
                valor = max(valor, 0)
            if predicciones and var not in ["et0_diaria", "radiacion_diaria", "precipitacion_diaria"]:
                valor = 0.7 * valor + 0.3 * predicciones[-1][var]
            pred[var] = float(round(valor, 3))
        predicciones.append(pred)
    return predicciones


def _evaluar_dia(d: dict) -> tuple[int, list[str]]:
    estres = float(d.get("estres_termico_medio") or 0)
    humedad = float(d.get("humedad_media") or 0)
    nivel = 0
    condiciones: list[str] = []
    if estres > 110:
        condiciones.append("estrés térmico crítico")
        nivel = max(nivel, 3)
    elif estres > 95:
        condiciones.append("estrés térmico alto")
        nivel = max(nivel, 2)
    if humedad > 90:
        condiciones.append("humedad extrema")
        nivel = max(nivel, 3)
    elif humedad > 85:
        condiciones.append("humedad elevada")
        nivel = max(nivel, 2)
    return nivel, condiciones


def get_alertas(db: Session) -> dict:
    reales = get_last_n_daily(db, 7)
    alertas_reales = []
    for d in reales:
        nivel, condiciones = _evaluar_dia(d)
        if nivel >= 2:
            alertas_reales.append(f"[{d['fecha']}] " + " · ".join(condiciones))

    pred = get_prediccion(db, 7)
    alertas_pred = []
    if isinstance(pred, list):
        for d in pred:
            nivel, condiciones = _evaluar_dia(d)
            if nivel >= 2:
                alertas_pred.append(f"[{d['fecha']}] Previsto: " + " · ".join(condiciones))

    return {
        "resumen": f"{len(alertas_reales)} día(s) con alertas recientes",
        "alertas_reales": alertas_reales,
        "alertas_prediccion": alertas_pred,
        "alertas_prioritarias": (alertas_reales + alertas_pred)[:5],
        "alertas_combinadas": alertas_pred[:2],
        "riesgo_acumulado": {
            "real": [a for a in alertas_reales if "estrés" in a.lower()][:3],
            "prediccion": [a for a in alertas_pred if "estrés" in a.lower()][:3],
            "combinado": [],
        },
    }


def get_recomendaciones(db: Session, dias: int = 7) -> dict:
    pred = get_prediccion(db, dias)
    if not isinstance(pred, list):
        return pred

    diario = []
    for i, dia in enumerate(pred):
        et0 = dia["et0_diaria"]
        estres = dia["estres_termico_medio"]
        humedad = dia["humedad_media"]
        recs = []
        if et0 > 4:
            recs.append("ET0 muy alta → aumentar riego.")
        elif et0 > 2:
            recs.append("ET0 moderada → riego medio.")
        else:
            recs.append("ET0 baja → riego ligero.")
        if estres > 110:
            recs.append("Estrés térmico crítico → ventilación y sombreo.")
        if humedad > 85:
            recs.append("Humedad elevada → vigilar hongos.")
        diario.append({
            "fecha": dia["fecha"],
            "et0": round(et0, 2),
            "estres": round(estres, 2),
            "humedad": round(humedad, 2),
            "lluvia": round(dia.get("precipitacion_diaria") or 0, 2),
            "recomendaciones": recs[:3],
        })

    et0_vals = [d["et0_diaria"] for d in pred]
    estres_vals = [d["estres_termico_medio"] for d in pred]
    humedad_vals = [d["humedad_media"] for d in pred]
    resumen_semanal = {
        "informacion": [
            f"ET0 semanal: {'sube' if et0_vals[-1] > et0_vals[0] else 'baja'}",
            f"Estrés semanal: {'sube' if estres_vals[-1] > estres_vals[0] else 'baja'}",
            f"Humedad semanal: {'sube' if humedad_vals[-1] > humedad_vals[0] else 'baja'}",
        ],
        "nivel_riesgo": "Semana estable" if max(estres_vals) < 95 else "Vigilar estrés térmico",
        "recomendacion_general": "Mantén estrategia de ventilación según alertas.",
    }

    fecha_max = get_max_fecha(db)
    resumen_mensual = {"informacion": ["Sin datos mensuales"], "nivel_riesgo": "—", "recomendacion_general": "—"}
    if fecha_max:
        inicio = fecha_max - timedelta(days=30)
        mes_rows = get_daily_between(db, inicio, fecha_max)
        if mes_rows:
            lluvia_total = sum(float(r.get("precipitacion_diaria") or 0) for r in mes_rows)
            resumen_mensual = {
                "informacion": [
                    f"Periodo: {inicio.isoformat()} → {fecha_max.isoformat()}",
                    f"Lluvia acumulada: {round(lluvia_total, 1)} mm",
                    f"Días con datos: {len(mes_rows)}",
                ],
                "nivel_riesgo": "Riesgo alto por lluvia" if lluvia_total > 40 else "Mes estable",
                "recomendacion_general": "Revisa ventilación si humedad persistente > 85%.",
            }

    return {"diario": diario, "resumen_semanal": resumen_semanal, "resumen_mensual": resumen_mensual}
