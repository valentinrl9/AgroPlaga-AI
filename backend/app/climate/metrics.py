"""Indicadores agroclimáticos NEXO (DPV, punto de rocío)."""

import math


def saturation_vapor_pressure_kpa(t_c: float) -> float:
    return 0.61078 * math.exp((17.27 * t_c) / (t_c + 237.3))


def calc_dpv_kpa(t_c: float, rh_pct: float) -> float:
    es = saturation_vapor_pressure_kpa(t_c)
    ea = es * (rh_pct / 100.0)
    return max(es - ea, 0.0)


def dpv_status(dpv: float) -> str:
    if dpv < 0.4:
        return "warning"
    if dpv > 1.6:
        return "critical"
    if 0.8 <= dpv <= 1.2:
        return "optimal"
    return "moderate"


def calc_dew_point_c(t_c: float, rh_pct: float) -> float:
    if rh_pct <= 0:
        return t_c
    a = math.log(rh_pct / 100.0)
    b = (17.27 * t_c) / (237.3 + t_c)
    return (237.3 * (a + b)) / (17.27 - (a + b))
