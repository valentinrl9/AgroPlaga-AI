from fastapi import APIRouter, Depends

from app.core.security import get_current_active_user
from app.data.plague_catalog import catalog_entries, load_catalog
from app.models.user import User

router = APIRouter()


@router.get("")
def list_plagues(_current_user: User = Depends(get_current_active_user)):
    catalog = load_catalog()
    return {
        "version": catalog["version"],
        "region": catalog["region"],
        "labels": catalog["labels"],
        "plagues": catalog_entries(),
    }
