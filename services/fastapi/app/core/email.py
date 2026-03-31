"""
Email Service — Asynchronous SMTP client for sending notifications.
Supports pure text and HTML emails using standard aiosmtplib.
"""

import logging
from email.message import EmailMessage
import aiosmtplib

from app.core.config import settings

logger = logging.getLogger("careremind.email")

class EmailService:
    def __init__(self):
        # We assume standard SMTP config in settings, or mock if missing
        self.hostname = getattr(settings, "SMTP_HOST", "smtp.gmail.com")
        self.port = getattr(settings, "SMTP_PORT", 587)
        self.username = getattr(settings, "SMTP_USERNAME", "")
        self.password = getattr(settings, "SMTP_PASSWORD", "")
        self.from_email = getattr(settings, "SMTP_FROM_EMAIL", "noreply@careremind.com")

    async def send_email(self, to_email: str, subject: str, content: str, is_html: bool = False):
        if not self.username or not self.password:
            logger.warning("SMTP credentials missing. Mocking email send to %s", to_email)
            logger.debug("Mock Email Subj: %s\nContent: %s", subject, content)
            return

        message = EmailMessage()
        message["From"] = self.from_email
        message["To"] = to_email
        message["Subject"] = subject
        
        if is_html:
            message.set_content("Please enable HTML to view this email.")
            message.add_alternative(content, subtype='html')
        else:
            message.set_content(content)

        try:
            await aiosmtplib.send(
                message,
                hostname=self.hostname,
                port=self.port,
                start_tls=True,
                username=self.username,
                password=self.password,
            )
            logger.info("Successfully sent email to %s", to_email)
        except Exception as e:
            logger.error("Failed to send email to %s: %s", to_email, str(e))

    async def send_welcome_email(self, to_email: str, doctor_name: str):
        subject = "Welcome to CareRemind!"
        content = f"""
        <html>
        <body>
            <h2>Welcome Dr. {doctor_name}!</h2>
            <p>Thank you for registering with CareRemind.</p>
            <p>You can now start automating patient reminders effortlessly.</p>
        </body>
        </html>
        """
        await self.send_email(to_email, subject, content, is_html=True)


email_service = EmailService()
