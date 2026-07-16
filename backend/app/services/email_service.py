"""Send email via configured SMTP."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.repositories.settings_store import get_smtp_settings


class EmailError(Exception):
    pass


def _send_raw(msg: EmailMessage | MIMEMultipart) -> None:
    cfg = get_smtp_settings()
    host = cfg.get("smtp_host")
    from_addr = cfg.get("smtp_from")
    if not host or not from_addr:
        raise EmailError(
            "SMTP is not configured — set host and from address in Admin → Email settings"
        )

    port = int(cfg.get("smtp_port") or 587)
    user = cfg.get("smtp_user") or ""
    password = cfg.get("smtp_password") or ""
    use_tls = bool(cfg.get("smtp_use_tls", True))

    try:
        if use_tls:
            with smtplib.SMTP(host, port, timeout=30) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                if user:
                    smtp.login(user, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=30) as smtp:
                if user:
                    smtp.login(user, password)
                smtp.send_message(msg)
    except smtplib.SMTPException as exc:
        raise EmailError(str(exc)) from exc


def send_email(*, to: str, subject: str, body: str) -> None:
    cfg = get_smtp_settings()
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = cfg.get("smtp_from")
    msg["To"] = to
    msg.set_content(body)
    _send_raw(msg)


def send_email_with_attachment(
    *,
    to: str,
    subject: str,
    body: str,
    attachment_bytes: bytes,
    attachment_name: str,
    mime_type: str = "application/pdf",
) -> None:
    cfg = get_smtp_settings()
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = cfg.get("smtp_from")
    msg["To"] = to
    msg.attach(MIMEText(body))
    part = MIMEApplication(attachment_bytes, _subtype=mime_type.split("/")[-1])
    part.add_header("Content-Disposition", "attachment", filename=attachment_name)
    msg.attach(part)
    _send_raw(msg)
