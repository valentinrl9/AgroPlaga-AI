from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_roles
from app.models.user import User
from app.models.scan import Scan
from app.models.outbreak_event import OutbreakEvent
from app.models.alert import Alert
from app.models.zone import AgriZone

router = APIRouter()

TECH_OR_ADMIN = require_roles(["tech", "admin"])


@router.get("/summary")
def stats_summary(
    current_user: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    return {
        "users": db.query(User).count(),
        "scans": db.query(Scan).count(),
        "outbreak_events": db.query(OutbreakEvent).count(),
        "alerts": db.query(Alert).count(),
        "zones": db.query(AgriZone).count(),
    }
