from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.rate_limit import check_rate_limit
from app.core.security import (
    create_token_pair,
    get_current_active_user,
    get_password_hash,
    revoke_user_tokens,
    verify_password,
    decode_refresh_token,
)
from app.models.user import User
from app.schemas.auth import RefreshRequest, Token, UserCreate, UserLogin
from app.services.invite_service import consume_invite

router = APIRouter()


def _issue_tokens(user: User) -> Token:
    access_token, refresh_token = create_token_pair(user)
    return Token(access_token=access_token, refresh_token=refresh_token)


def _rate_limit_auth(request: Request, email: str) -> None:
    from app.core.rate_limit import client_ip, check_rate_limit

    check_rate_limit(f"auth:{client_ip(request)}:{email.lower()}")


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    _rate_limit_auth(request, user_data.email)
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    role = "farmer"
    if settings.registration_mode == "invite_only":
        if not user_data.invite_code or not user_data.invite_code.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Se requiere un código de invitación para registrarse.",
            )
        try:
            invite = consume_invite(db, user_data.invite_code)
            role = invite.role
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=role,
        consent_accepted_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.flush()
    if settings.registration_mode == "invite_only" and user_data.invite_code:
        invite.redeemed_by_user_id = user.id
        db.add(invite)
    db.commit()
    db.refresh(user)
    return _issue_tokens(user)


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    _rate_limit_auth(request, credentials.email)
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta desactivada")
    return _issue_tokens(user)


@router.post("/token", response_model=Token)
def token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    _rate_limit_auth(request, form_data.username)
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta desactivada")
    return _issue_tokens(user)


@router.post("/refresh", response_model=Token)
def refresh(body: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    from app.core.rate_limit import rate_limit_request

    rate_limit_request(request, "auth-refresh", max_attempts=30, window_seconds=60)
    email, token_version = decode_refresh_token(body.refresh_token)
    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if token_version != (user.token_version or 0):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return _issue_tokens(user)


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    revoke_user_tokens(current_user)
    db.add(current_user)
    db.commit()
    return {"ok": True}
