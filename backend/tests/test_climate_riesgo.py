"""Tests for climate riesgo logic."""

from app.climate.service import _riesgo_dia_pct, dew_point_status


def test_riesgo_dia_pct_range():
    assert 0 <= _riesgo_dia_pct(50, 60) <= 100
    assert _riesgo_dia_pct(120, 95) >= _riesgo_dia_pct(40, 70)


def test_dew_point_status():
    assert dew_point_status(18, 20) == "critical"
    assert dew_point_status(16, 20) == "warning"
    assert dew_point_status(10, 20) == "optimal"
