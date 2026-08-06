"""Notificación por email de solicitudes de contacto / piloto."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)

INTEREST_LABELS = {
    "scan": "Scanner IA offline",
    "mapa": "Mapa comarcal / alertas",
    "panel": "Panel cooperativa",
    "mapa-dosis": "Vademécum MAPA y dosis",
}

ROLE_LABELS = {
    "agricultor": "Agricultor",
    "tecnico": "Técnico / perito",
    "cooperativa": "Cooperativa",
    "otro": "Otro",
}


def format_inquiry_body(
    *,
    name: str,
    email: str,
    role: str,
    organization: str,
    phone: str,
    interest: str,
) -> str:
    role_label = ROLE_LABELS.get(role, role)
    interest_label = INTEREST_LABELS.get(interest, interest)
    return (
        f"Nueva solicitud de piloto — AgroPlaga\n\n"
        f"Nombre: {name}\n"
        f"Email: {email}\n"
        f"Perfil: {role_label}\n"
        f"Organización: {organization}\n"
        f"Teléfono: {phone}\n"
        f"Interés principal: {interest_label}\n"
    )


def send_contact_notification(
    *,
    name: str,
    email: str,
    role: str,
    organization: str,
    phone: str,
    interest: str,
) -> bool:
    """Envía email al administrador. Devuelve True si se envió correctamente."""
    notify_to = settings.contact_notify_email
    if not notify_to:
        logger.warning("CONTACT_NOTIFY_EMAIL no configurado; email no enviado")
        return False

    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP incompleto; email no enviado (datos guardados en BD)")
        return False

    body = format_inquiry_body(
        name=name,
        email=email,
        role=role,
        organization=organization,
        phone=phone,
        interest=interest,
    )
    msg = EmailMessage()
    msg["Subject"] = f"[AgroPlaga Piloto] {name} — {ROLE_LABELS.get(role, role)}"
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = notify_to
    msg["Reply-To"] = email
    msg.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
        logger.info("Email de contacto enviado a %s", notify_to)
        return True
    except Exception:
        logger.exception("Error enviando email de contacto")
        return False
