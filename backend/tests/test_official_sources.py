"""Tests for official sources catalog."""

from app.services.official_sources_service import (
    format_alert_attribution,
    format_official_attribution,
    resolve_official_sources,
)


def test_format_official_attribution_raif():
    sources = resolve_official_sources(plague="trips", crop="pimiento", context="recommendation")
    text = format_official_attribution(sources)
    assert text.startswith("Según información oficial de")
    assert "Andalucía" in text or "RAIF" in text or "Junta" in text


def test_format_alert_attribution():
    sources = resolve_official_sources(plague="mosca blanca", context="alert", include_community=True)
    text = format_alert_attribution(sources)
    assert "oficial" in text.lower() or "NEXO" in text


def test_resolve_raif_for_trips_almeria():
    sources = resolve_official_sources(plague="trips", crop="pimiento", context="recommendation")
    ids = {item["id"] for item in sources}
    assert "raif-portal" in ids
    assert "raif-horticolas-almeria" in ids
    assert any(item["kind"] == "official_protocol" for item in sources)


def test_alert_includes_community_source():
    sources = resolve_official_sources(plague="mosca blanca", context="alert", include_community=True)
    ids = {item["id"] for item in sources}
    assert "nexo-community-map" in ids
    assert "raif-portal" in ids
