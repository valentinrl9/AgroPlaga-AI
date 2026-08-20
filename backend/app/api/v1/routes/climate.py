from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.climate import service as climate_service
from app.climate.config import CLIMATE_PREVIEW_OPEN
from app.climate.etl import run_climate_etl
from app.core.security import get_current_active_admin, get_current_active_user
from app.models.user import User

router = APIRouter()


def _require_climate(user: User = Depends(get_current_active_user)) -> User:
    if not climate_service.user_has_climate_access(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Módulo NEXO Climate requiere paquete premium (climate o field premium).",
        )
    return user


def _climate_kwargs(
    db: Session,
    user: User,
    farm_id: int | None,
    zone_id: int | None,
    station_id: int | None,
) -> dict:
    try:
        zone_id, station_id_override = climate_service.resolve_climate_params(
            db, user, farm_id, zone_id, station_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {
        "zone_id": zone_id,
        "station_id_override": station_id_override,
        "farm_id": farm_id,
        "user": user,
    }


@router.get("/stations")
def list_stations(db: Session = Depends(get_db), _user: User = Depends(_require_climate)):
    return climate_service.get_stations(db)


@router.get("/health")
def climate_health(
    farm_id: int | None = Query(default=None),
    zone_id: int | None = Query(default=None),
    station_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(_require_climate),
):
    return climate_service.get_health(db, **_climate_kwargs(db, user, farm_id, zone_id, station_id))


@router.get("/etl/status")
def etl_status(_user: User = Depends(_require_climate)):
    return climate_service.get_etl_status()


@router.post("/etl/run")
def etl_run(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_active_admin),
):
    try:
        elapsed = run_climate_etl(db)
        return {"success": True, "elapsed_s": round(elapsed, 1)}
    except Exception as exc:
        from app.core.api_errors import safe_http_error

        raise safe_http_error(exc, public_message="Error al ejecutar ETL de clima") from exc


@router.get("/actual")
def actual(
    farm_id: int | None = Query(default=None),
    zone_id: int | None = Query(default=None),
    station_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(_require_climate),
):
    data = climate_service.get_actual(db, **_climate_kwargs(db, user, farm_id, zone_id, station_id))
    if data.get("error"):
        raise HTTPException(status_code=503, detail=data["error"])
    return data


@router.get("/prediccion")
def prediccion(
    dias: int = 7,
    farm_id: int | None = Query(default=None),
    zone_id: int | None = Query(default=None),
    station_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(_require_climate),
):
    result = climate_service.get_prediccion(
        db, dias=dias, **_climate_kwargs(db, user, farm_id, zone_id, station_id)
    )
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=503, detail=result["error"])
    return result


@router.get("/recomendaciones")
def recomendaciones(
    dias: int = 7,
    farm_id: int | None = Query(default=None),
    zone_id: int | None = Query(default=None),
    station_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(_require_climate),
):
    return climate_service.get_recomendaciones(
        db, dias=dias, **_climate_kwargs(db, user, farm_id, zone_id, station_id)
    )


@router.get("/alertas")
def alertas(
    farm_id: int | None = Query(default=None),
    zone_id: int | None = Query(default=None),
    station_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(_require_climate),
):
    return climate_service.get_alertas(db, **_climate_kwargs(db, user, farm_id, zone_id, station_id))


@router.get("/riesgo")
def riesgo(
    dias: int = 7,
    farm_id: int | None = Query(default=None),
    zone_id: int | None = Query(default=None),
    station_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(_require_climate),
):
    result = climate_service.get_riesgo_semanal(
        db, dias=dias, **_climate_kwargs(db, user, farm_id, zone_id, station_id)
    )
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=503, detail=result["error"])
    return result


@router.get("/access")
def climate_access(user: User = Depends(get_current_active_user)):
    return {
        "has_climate_module": user.has_climate_module,
        "has_field_premium": user.has_field_premium,
        "climate_accessible": climate_service.user_has_climate_access(user),
        "preview_open": CLIMATE_PREVIEW_OPEN,
    }
