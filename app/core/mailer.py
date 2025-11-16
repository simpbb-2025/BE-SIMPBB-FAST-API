from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
import smtplib

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.core.config import settings


def _build_message(subject: str, recipient: str, body: str, html_body: str | None = None) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.mail_from
    message["To"] = recipient
    message.set_content(body)
    if html_body:
        message.add_alternative(html_body, subtype="html")
    return message


def _send_message_sync(message: EmailMessage) -> None:
    if not settings.mail_server:
        raise RuntimeError("Mail server is not configured")

    if settings.mail_ssl_tls:
        smtp_class = smtplib.SMTP_SSL
    else:
        smtp_class = smtplib.SMTP

    with smtp_class(settings.mail_server, settings.mail_port) as server:
        if settings.mail_starttls and not settings.mail_ssl_tls:
            server.starttls()

        if settings.mail_use_credentials and settings.mail_username:
            server.login(settings.mail_username, settings.mail_password or "")

        server.send_message(message)


async def send_email(subject: str, recipient: str, body: str, html_body: str | None = None) -> None:
    """Send an email asynchronously using the configured SMTP server."""

    message = _build_message(subject, recipient, body, html_body)
    await asyncio.to_thread(_send_message_sync, message)


async def send_registration_code_email(recipient: str, code: str, expires_at: datetime) -> None:
    def _to_local(dt: datetime) -> tuple[str, str]:
        tz_name = settings.timezone or "Asia/Jakarta"
        try:
            tz = ZoneInfo(tz_name)
        except ZoneInfoNotFoundError:
            tz = timezone(timedelta(hours=7))

        if dt.tzinfo is None:
            base = dt.replace(tzinfo=timezone.utc)
        else:
            base = dt.astimezone(timezone.utc)

        localized = base.astimezone(tz)
        offset = localized.utcoffset() or timedelta(0)
        total_minutes = int(offset.total_seconds() // 60)
        sign = "+" if total_minutes >= 0 else "-"
        total_minutes = abs(total_minutes)
        hours, minutes = divmod(total_minutes, 60)
        if tz_name == "Asia/Jakarta":
            formatted = localized.strftime("%d %B %Y %H:%M WIB")
            label = ""
        else:
            formatted = localized.strftime("%d %B %Y %H:%M")
            if minutes:
                label = f" (UTC{sign}{hours:02d}:{minutes:02d})"
            else:
                label = f" (UTC{sign}{hours:02d})"
        return formatted, label

    formatted_time, offset_label = _to_local(expires_at)
    subject = "Kode Verifikasi Registrasi SIMPBB"
    text_body = f"""Halo,

Berikut kode verifikasi registrasi SIMPBB Anda:

    Kode             : {code}
    Berlaku sampai   : {formatted_time}{offset_label}

Masukkan kode ini pada form registrasi SIMPBB untuk melanjutkan proses pembuatan akun.
Jika Anda tidak merasa meminta kode ini, abaikan email ini dan akun Anda tetap aman.

Terima kasih,
Tim SIMPBB
"""
    html_body = f"""
<!DOCTYPE html>
<html lang="id">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Kode Verifikasi SIMPBB</title>
    <style>
      body {{
        margin: 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f8fafc;
        color: #0f172a;
      }}
      .container {{
        max-width: 520px;
        margin: 0 auto;
        padding: 32px 24px;
      }}
      .card {{
        background-color: #ffffff;
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
        border: 1px solid #e2e8f0;
      }}
      .badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: #ecfeff;
        color: #0e7490;
        font-size: 12px;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 999px;
        letter-spacing: 0.05em;
      }}
      h1 {{
        font-size: 24px;
        margin: 24px 0 12px;
      }}
      p {{
        margin: 0 0 16px;
        line-height: 1.6;
      }}
      .code-box {{
        margin: 24px 0;
        border-radius: 14px;
        background: linear-gradient(135deg, #2563eb, #4f46e5);
        color: #ffffff;
        padding: 24px;
        text-align: center;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.25);
      }}
      .code-label {{
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        opacity: 0.85;
      }}
      .code-value {{
        font-size: 32px;
        font-weight: 700;
        letter-spacing: 0.2em;
        margin-top: 8px;
      }}
      .meta {{
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 20px;
        border-radius: 12px;
        background-color: #f1f5f9;
      }}
      .meta span {{
        font-size: 14px;
        color: #475569;
      }}
      .meta strong {{
        color: #0f172a;
        font-weight: 600;
      }}
      .footer {{
        margin-top: 32px;
        border-top: 1px solid #e2e8f0;
        padding-top: 20px;
        font-size: 13px;
        color: #64748b;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="card">
        <span class="badge">SIMPBB · Verifikasi Akun</span>
        <h1>Verifikasi Pendaftaran Anda</h1>
        <p>Gunakan kode berikut untuk menyelesaikan proses registrasi di SIMPBB.</p>

        <div class="code-box">
          <div class="code-label">Kode Verifikasi</div>
          <div class="code-value">{code}</div>
        </div>

        <div class="meta">
          <span>⚡ Berlaku sampai <strong>{formatted_time}{offset_label}</strong></span>
          <span>🔐 Demi keamanan akun Anda, jangan membagikan kode ini kepada siapa pun.</span>
        </div>

        <p>
          Masukkan kode di atas pada form registrasi SIMPBB. Jika Anda tidak pernah meminta kode
          ini, abaikan email ini dan akun Anda tetap aman.
        </p>

        <div class="footer">
          Terima kasih,<br />
          <strong>Tim SIMPBB</strong>
        </div>
      </div>
    </div>
  </body>
</html>
"""
    await send_email(subject, recipient, text_body, html_body)
