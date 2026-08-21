"""Tests resolución estaciones Climate sur Almería."""

from app.climate.stations import _haversine_km, resolve_station, station_to_dict
from app.db.seed_climate_stations import seed_climate_stations
from app.models.climate_station import ClimateStation
from app.models.zone import AgriZone


def test_haversine_positive():
    d = _haversine_km(36.77, -2.81, 36.83, -2.87)
    assert d > 0


def test_seed_and_list_stations(client):
    seed_climate_stations()
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        stations = db.query(ClimateStation).filter(ClimateStation.active.is_(True)).all()
        assert len(stations) >= 10
        slugs = {s.slug for s in stations}
        assert "poniente" in slugs
        assert "adra" in slugs
        assert "roquetas" in slugs
    finally:
        db.close()


def test_resolve_station_default(client):
    seed_climate_stations()
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        station = resolve_station(db, None)
        assert station.slug == "poniente"
    finally:
        db.close()


def test_resolve_station_by_zone_id(client):
    seed_climate_stations()
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        zone = db.query(AgriZone).filter(AgriZone.name == "Roquetas de Mar").first()
        assert zone is not None
        station = resolve_station(db, zone.id)
        assert station.slug == "roquetas"
        payload = station_to_dict(station, zone_name=zone.name)
        assert payload["zone_id"] == zone.id
    finally:
        db.close()


def test_climate_stations_api(client, unique_email):
    from tests.conftest import auth_headers, register_and_login

    seed_climate_stations()
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)

    response = client.get("/api/v1/climate/stations", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) >= 10
    assert any(s["slug"] == "vicar" for s in body)


def test_resolve_station_with_override(client):
    seed_climate_stations()
    from app.db.session import SessionLocal
    from app.climate.stations import resolve_station_with_override

    db = SessionLocal()
    try:
        adra = db.query(ClimateStation).filter(ClimateStation.slug == "adra").first()
        poniente = db.query(ClimateStation).filter(ClimateStation.slug == "poniente").first()
        assert adra is not None and poniente is not None
        manual, auto = resolve_station_with_override(db, None, adra.id)
        assert manual.slug == "adra"
        assert auto.slug == "poniente"
    finally:
        db.close()


def test_climate_actual_with_zone_id(client, unique_email):
    from tests.conftest import auth_headers, register_and_login

    seed_climate_stations()
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)

    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        zone = db.query(AgriZone).filter(AgriZone.name == "Níjar").first()
        assert zone is not None
        zone_id = zone.id
    finally:
        db.close()

    response = client.get(f"/api/v1/climate/health?zone_id={zone_id}", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["station"]["slug"] == "nijar"


def test_climate_actual_uses_farm_station_override(client, unique_email):
    from tests.conftest import auth_headers, register_and_login

    seed_climate_stations()
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)

    from app.db.session import SessionLocal
    from app.models.farm import Farm
    from app.models.user import User

    db = SessionLocal()
    try:
        zone = db.query(AgriZone).filter(AgriZone.name == "El Ejido").first()
        adra = db.query(ClimateStation).filter(ClimateStation.slug == "adra").first()
        user = db.query(User).filter(User.email == unique_email).first()
        assert zone is not None and adra is not None and user is not None

        farm = Farm(
            user_id=user.id,
            name="Finca test clima",
            crop="tomate",
            farm_type="greenhouse",
            zone_id=zone.id,
            climate_station_id=adra.id,
        )
        db.add(farm)
        db.commit()
        db.refresh(farm)
        farm_id = farm.id
    finally:
        db.close()

    response = client.get(f"/api/v1/climate/health?farm_id={farm_id}", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["station"]["slug"] == "adra"
    assert body["auto_station"]["slug"] == "poniente"
    assert body["station_manual_override"] is True
