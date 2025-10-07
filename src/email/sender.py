"""
Email sender for notification system
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from datetime import datetime, timezone
import os

logger = logging.getLogger(__name__)


class EmailSender:
    """
    Email sender for notifications (SMTP-based)
    """
    
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        use_tls: bool = True,
        enabled: bool = None
    ):
        """
        Initialize email sender
        
        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: Sender email address
            use_tls: Whether to use TLS
            enabled: Whether email notifications are enabled
        """
        # Load from environment if not provided
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.from_email = from_email or os.getenv("FROM_EMAIL", "noreply@bookgen.com")
        self.use_tls = use_tls
        
        # Email is only enabled if explicitly set or if SMTP credentials are configured
        if enabled is not None:
            self.enabled = enabled
        else:
            self.enabled = bool(self.smtp_host and self.smtp_user and self.smtp_password)
        
        if self.enabled:
            logger.info(f"Email notifications enabled: {self.smtp_host}:{self.smtp_port}")
        else:
            logger.info("Email notifications disabled (no SMTP configuration)")
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not self.enabled:
            logger.warning("Email sending attempted but email is disabled")
            return False, "Email notifications are disabled"
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Date'] = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
            
            # Add plain text part
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML part if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True, None
        
        except Exception as e:
            error_msg = f"Failed to send email to {to_email}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def send_completion_notification(
        self,
        to_email: str,
        job_id: str,
        biography_id: int,
        character_name: str,
        status: str
    ) -> tuple[bool, Optional[str]]:
        """
        Send job completion email notification
        
        Args:
            to_email: Recipient email
            job_id: Job identifier
            biography_id: Biography ID
            character_name: Character name
            status: Job status
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        subject = f"BookGen: Biography Generation {'Completed' if status == 'completed' else 'Failed'}"
        
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
        severity: str = "error"
    ) -> tuple[bool, Optional[str]]:
        """
        Send error alert email
        
        Args:
            to_email: Recipient email
            job_id: Job identifier
            error: Error message
            severity: Error severity
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
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
        metadata: Optional[dict] = None
    ) -> List[tuple[str, bool, Optional[str]]]:
        """
        Send alert to administrators
        
        Args:
            admin_emails: List of admin email addresses
            alert_type: Type of alert
            message: Alert message
            metadata: Optional metadata
        
        Returns:
            List of tuples (email, success, error_message)
        """
        subject = f"BookGen Admin Alert: {alert_type}"
        
        metadata_str = ""
        if metadata:
            metadata_str = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
        
        body = f"""
Administrative Alert from BookGen

Alert Type: {alert_type}
Message: {message}

{metadata_str if metadata_str else ''}

Timestamp: {datetime.now(timezone.utc).isoformat()}

BookGen System
        """
        
        results = []
        for email in admin_emails:
            success, error = self._send_email(email, subject, body.strip())
            results.append((email, success, error))
        
        return results
