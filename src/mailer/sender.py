"""
Mailer sender for notification system, relocated from src.email to avoid clashing
with Python's standard library email package.
"""

# The implementation is identical to the previous src.email.sender module.
# It has been moved here so that importing the standard library ``email``
# package continues to work correctly (the old src/email package shadowed it).

import logging
import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

logger = logging.getLogger(__name__)


class EmailSender:
    """SMTP-based email sender used by the notification system."""

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        use_tls: bool = True,
        enabled: bool = None,
    ) -> None:
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.from_email = from_email or os.getenv("FROM_EMAIL", "noreply@bookgen.com")
        self.use_tls = use_tls

        if enabled is not None:
            self.enabled = enabled
        else:
            self.enabled = bool(self.smtp_host and self.smtp_user and self.smtp_password)

        if self.enabled:
            logger.info("Email notifications enabled: %s:%s", self.smtp_host, self.smtp_port)
        else:
            logger.info("Email notifications disabled (no SMTP configuration)")

    def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        if not self.enabled:
            logger.warning("Email sending attempted but email is disabled")
            return False, "Email notifications are disabled"

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg["Date"] = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

            msg.attach(MIMEText(body, "plain"))
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info("Email sent successfully to %s", to_email)
            return True, None
        except Exception as exc:  # pragma: no cover - logging side effect
            error_msg = f"Failed to send email to {to_email}: {exc}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def send_completion_notification(
        self,
        to_email: str,
        job_id: str,
        biography_id: int,
        character_name: str,
        status: str,
    ) -> tuple[bool, Optional[str]]:
        subject = (
            "BookGen: Biography Generation Completed"
            if status == "completed"
            else "BookGen: Biography Generation Failed"
        )
        body = f"""
Hello,

Your biography generation for "{character_name}" has {status}.

Job ID: {job_id}
Biography ID: {biography_id}
Status: {status}
Timestamp: {datetime.now(timezone.utc).isoformat()}

Thank you for using BookGen!

Best regards,
BookGen Team
"""
        html_body = f"""
<html>
<body>
    <h2>BookGen Notification</h2>
    <p>Your biography generation for <strong>"{character_name}"</strong> has <strong>{status}</strong>.</p>
    <ul>
        <li><strong>Job ID:</strong> {job_id}</li>
        <li><strong>Biography ID:</strong> {biography_id}</li>
        <li><strong>Status:</strong> {status}</li>
        <li><strong>Timestamp:</strong> {datetime.now(timezone.utc).isoformat()}</li>
    </ul>
    <p>Thank you for using BookGen!</p>
    <p>Best regards,<br>BookGen Team</p>
</body>
</html>
"""
        return self._send_email(to_email, subject, body.strip(), html_body.strip())

    def send_error_alert(
        self,
        to_email: str,
        job_id: str,
        error: str,
        severity: str = "error",
    ) -> tuple[bool, Optional[str]]:
        subject = f"BookGen Alert [{severity.upper()}]: Job {job_id}"
        body = f"""
Alert from BookGen System

Severity: {severity.upper()}
Job ID: {job_id}
Error: {error}
Timestamp: {datetime.now(timezone.utc).isoformat()}

Please check the system logs for more details.

BookGen System
"""
        html_body = f"""
<html>
<body>
    <h2 style="color: red;">BookGen Alert</h2>
    <p><strong>Severity:</strong> <span style="color: red;">{severity.upper()}</span></p>
    <p><strong>Job ID:</strong> {job_id}</p>
    <p><strong>Error:</strong> {error}</p>
    <p><strong>Timestamp:</strong> {datetime.now(timezone.utc).isoformat()}</p>
    <p>Please check the system logs for more details.</p>
</body>
</html>
"""
        return self._send_email(to_email, subject, body.strip(), html_body.strip())

    def send_admin_alert(
        self,
        admin_emails: List[str],
        alert_type: str,
        message: str,
        metadata: Optional[dict] = None,
    ) -> List[tuple[str, bool, Optional[str]]]:
        subject = f"BookGen Admin Alert: {alert_type}"
        metadata_str = ""
        if metadata:
            metadata_str = "\n".join(f"{key}: {value}" for key, value in metadata.items())

        body = f"""
Administrative Alert from BookGen

Alert Type: {alert_type}
Message: {message}

{metadata_str if metadata_str else ''}

Timestamp: {datetime.now(timezone.utc).isoformat()}

BookGen System
"""
        results: List[tuple[str, bool, Optional[str]]] = []
        for email in admin_emails:
            success, error = self._send_email(email, subject, body.strip())
            results.append((email, success, error))
        return results
