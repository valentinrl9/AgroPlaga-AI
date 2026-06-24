from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user
from app.models.feedback import Feedback
from app.models.scan import Scan
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackRead
from app.services.gamification_service import check_feedback_badges

router = APIRouter()


@router.post("", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    body: FeedbackCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    scan = db.query(Scan).filter(Scan.id == body.scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escaneo no encontrado")
    if scan.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes valorar este escaneo")

    if not body.is_correct and not body.corrected_plague and not (body.comment and body.comment.strip()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indica un comentario si el diagnóstico no fue útil",
        )

    entry = Feedback(
        scan_id=body.scan_id,
        user_id=current_user.id,
        is_correct=body.is_correct,
        corrected_plague=body.corrected_plague.strip().lower() if body.corrected_plague else None,
        comment=body.comment,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    check_feedback_badges(db, current_user.id)
    return entry


@router.get("", response_model=list[FeedbackRead])
def list_my_feedback(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Feedback)
        .filter(Feedback.user_id == current_user.id)
        .order_by(Feedback.created_at.desc())
        .limit(50)
        .all()
    )
