from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.rate_limit import check_rate_limit
from app.models.contact_inquiry import ContactInquiry
from app.schemas.contact import ContactAck, ContactCreate
from app.services.contact_email_service import format_inquiry_body, send_contact_notification

router = APIRouter()

_ALLOWED_ROLES = {"agricultor", "tecnico", "cooperativa", "otro"}
_ALLOWED_INTERESTS = {"scan", "mapa", "panel", "mapa-dosis"}


def _rate_limit_contact(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(f"contact:{client_ip}", max_attempts=5, window_seconds=300)


@router.post("", response_model=ContactAck, status_code=status.HTTP_201_CREATED)
def submit_contact(body: ContactCreate, request: Request, db: Session = Depends(get_db)):
    _rate_limit_contact(request)

    role = body.role.strip().lower()
    if role not in _ALLOWED_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rol no válido")

    interest = body.interest.strip().lower()
    if interest not in _ALLOWED_INTERESTS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Interés no válido")

    message = format_inquiry_body(
        name=body.name.strip(),
        email=body.email.strip().lower(),
        role=role,
        organization=body.organization.strip(),
        phone=body.phone.strip(),
        interest=interest,
    )

    entry = ContactInquiry(
        name=body.name.strip(),
        email=body.email.strip().lower(),
        role=role,
        message=message,
    )
    db.add(entry)
    db.commit()

    send_contact_notification(
        name=body.name.strip(),
        email=body.email.strip().lower(),
        role=role,
        organization=body.organization.strip(),
        phone=body.phone.strip(),
        interest=interest,
    )

    return ContactAck()
