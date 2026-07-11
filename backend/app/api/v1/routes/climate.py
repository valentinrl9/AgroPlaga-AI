from fastapi import APIRouter, Depends, HTTPException, status
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
            detail="Módulo NEXO Climate no activo para esta cuenta.",
        )
    return user


@router.get("/health")
def climate_health(db: Session = Depends(get_db), _user: User = Depends(_require_climate)):
    return climate_service.get_health(db)


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
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/actual")
def actual(db: Session = Depends(get_db), _user: User = Depends(_require_climate)):
    data = climate_service.get_actual(db)
    if data.get("error"):
        raise HTTPException(status_code=503, detail=data["error"])
    return data


@router.get("/prediccion")
def prediccion(dias: int = 7, db: Session = Depends(get_db), _user: User = Depends(_require_climate)):
    result = climate_service.get_prediccion(db, dias=dias)
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=503, detail=result["error"])
    return result


@router.get("/recomendaciones")
def recomendaciones(dias: int = 7, db: Session = Depends(get_db), _user: User = Depends(_require_climate)):
    return climate_service.get_recomendaciones(db, dias=dias)


@router.get("/alertas")
def alertas(db: Session = Depends(get_db), _user: User = Depends(_require_climate)):
    return climate_service.get_alertas(db)


@router.get("/access")
def climate_access(user: User = Depends(get_current_active_user)):
    return {
        "has_climate_module": user.has_climate_module,
        "climate_accessible": climate_service.user_has_climate_access(user),
        "preview_open": CLIMATE_PREVIEW_OPEN,
    }
