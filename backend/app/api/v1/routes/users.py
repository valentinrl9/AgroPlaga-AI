from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_admin, get_current_active_user
from app.models.user import User
from app.schemas.user import UserRead, UserRoleUpdate

router = APIRouter()


@router.get("/me", response_model=UserRead)
def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.patch("/{user_id}/role", response_model=UserRead)
def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    valid_roles = {"farmer", "tech", "admin"}
    new_role = role_update.role.strip().lower()
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role must be one of: {', '.join(sorted(valid_roles))}",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.role = new_role
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
