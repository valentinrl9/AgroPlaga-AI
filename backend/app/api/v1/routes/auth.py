from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.rate_limit import check_rate_limit
from app.core.security import create_token_pair, get_password_hash, verify_password, decode_refresh_token
from app.models.user import User
from app.schemas.auth import RefreshRequest, Token, UserCreate, UserLogin

router = APIRouter()


def _issue_tokens(user: User) -> Token:
    access_token, refresh_token = create_token_pair(user.email)
    return Token(access_token=access_token, refresh_token=refresh_token)


def _rate_limit_auth(request: Request, email: str) -> None:
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(f"auth:{client_ip}:{email.lower()}")


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    _rate_limit_auth(request, user_data.email)
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role="farmer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _issue_tokens(user)


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    _rate_limit_auth(request, credentials.email)
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
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
    return _issue_tokens(user)


@router.post("/refresh", response_model=Token)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    email = decode_refresh_token(body.refresh_token)
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return _issue_tokens(user)
