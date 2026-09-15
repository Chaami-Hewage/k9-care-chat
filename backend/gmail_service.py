"""
Gmail Service — sends formatted health notification emails via the Gmail API.
Uses the Gmail API v1. Free for personal use.
"""
import logging
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any

from googleapiclient.discovery import build

from google_auth import GoogleAuthService

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────
# HTML Email Template
# ──────────────────────────────────────────────────────────────────────

def _email_template(title: str, body_html: str, footer_note: str = "") -> str:
    """Generate a branded K9 Care HTML email."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0; padding:0; background-color:#f0f0f5; font-family:'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f0f0f5; padding:32px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.08);">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); padding:32px 40px; text-align:center;">
                                <div style="font-size:36px; margin-bottom:8px;">🐾</div>
                                <h1 style="color:#ffffff; font-size:24px; margin:0; font-weight:700;">K9 Care Chat</h1>
                                <p style="color:rgba(255,255,255,0.85); font-size:14px; margin:4px 0 0;">Your Veterinary AI Assistant</p>
                            </td>
                        </tr>
                        <!-- Title -->
                        <tr>
                            <td style="padding:28px 40px 8px;">
                                <h2 style="color:#1e1b4b; font-size:20px; margin:0; font-weight:600;">{title}</h2>
                            </td>
                        </tr>
                        <!-- Body -->
                        <tr>
                            <td style="padding:12px 40px 28px; color:#374151; font-size:15px; line-height:1.7;">
                                {body_html}
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="padding:20px 40px; background-color:#f9fafb; border-top:1px solid #e5e7eb;">
                                <p style="color:#9ca3af; font-size:12px; margin:0; text-align:center;">
                                    {footer_note if footer_note else "This email was sent by Dr. Paws — K9 Care Chat AI Assistant."}
                                    <br>⚠️ This is AI-generated guidance. Always consult a licensed veterinarian.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


class GmailService:
    """Sends formatted emails via Google Gmail API."""

    def __init__(self, auth_service: GoogleAuthService):
        self.auth = auth_service

    def _get_service(self, email: str):
        """Get authenticated Gmail API service for a user."""
        credentials = self.auth.get_credentials(email)
        if not credentials:
            return None
        return build("gmail", "v1", credentials=credentials)

    def _send_email(self, from_email: str, to_email: str, subject: str, html_body: str) -> Optional[Dict[str, Any]]:
        """Send an email via Gmail API."""
        service = self._get_service(from_email)
        if not service:
            return None

        try:
            message = MIMEMultipart("alternative")
            message["to"] = to_email
            message["from"] = from_email
            message["subject"] = subject

            # Plain text fallback
            plain_text = f"K9 Care Chat Notification\n\n{subject}\n\nPlease view this email in HTML format for the full content."
            message.attach(MIMEText(plain_text, "plain"))
            message.attach(MIMEText(html_body, "html"))

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            sent = service.users().messages().send(
                userId="me",
                body={"raw": raw}
            ).execute()

            logger.info(f"Email sent: {subject} -> {to_email} (ID: {sent['id']})")
            return {"message_id": sent["id"], "to": to_email, "subject": subject}

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return None

    def send_vaccine_reminder_email(
        self,
        user_email: str,
        dog_name: str,
        vaccine_name: str,
        due_date: str,
        notes: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Send a vaccine reminder notification email."""
        body_html = f"""
        <p>Hi there! 👋</p>
        <p>This is a friendly reminder that <strong>{dog_name}</strong> has an upcoming vaccine:</p>

        <div style="background:#f0fdf4; border-left:4px solid #22c55e; padding:16px 20px; border-radius:8px; margin:16px 0;">
            <p style="margin:0; font-size:16px; font-weight:600; color:#166534;">💉 {vaccine_name}</p>
            <p style="margin:4px 0 0; color:#15803d;">📅 Due: {due_date}</p>
            <p style="margin:4px 0 0; color:#15803d;">🐶 Dog: {dog_name}</p>
        </div>

        {'<p style="color:#6b7280;">📝 <em>' + notes + '</em></p>' if notes else ''}

        <p>Please schedule an appointment with your veterinarian to ensure {dog_name} stays up to date on vaccinations.</p>
        <p>Stay paw-some! 🐾</p>
        """

        return self._send_email(
            from_email=user_email,
            to_email=user_email,
            subject=f"💉 Vaccine Reminder: {vaccine_name} for {dog_name}",
            html_body=_email_template(
                title=f"Vaccine Reminder for {dog_name}",
                body_html=body_html,
            ),
        )

    def send_emergency_alert_email(
        self,
        user_email: str,
        dog_name: str,
        symptoms: str,
        urgency: str = "high",
    ) -> Optional[Dict[str, Any]]:
        """Send an emergency health alert email."""
        urgency_color = "#dc2626" if urgency == "critical" else "#f59e0b"
        urgency_label = "🔴 CRITICAL" if urgency == "critical" else "🟡 HIGH"

        body_html = f"""
        <div style="background:#fef2f2; border-left:4px solid {urgency_color}; padding:16px 20px; border-radius:8px; margin:0 0 16px;">
            <p style="margin:0; font-size:16px; font-weight:700; color:#991b1b;">{urgency_label} — Emergency Alert</p>
        </div>

        <p>An emergency health concern has been flagged for <strong>{dog_name}</strong>:</p>

        <div style="background:#fff7ed; border-left:4px solid #f97316; padding:16px 20px; border-radius:8px; margin:16px 0;">
            <p style="margin:0; color:#9a3412;"><strong>Reported symptoms/concern:</strong></p>
            <p style="margin:4px 0 0; color:#c2410c;">{symptoms}</p>
        </div>

        <p><strong>⚡ Recommended action:</strong></p>
        <ul style="color:#374151;">
            <li>Contact your veterinarian or emergency vet clinic <strong>immediately</strong></li>
            <li>Keep {dog_name} calm and comfortable</li>
            <li>Do not attempt home treatment for serious symptoms</li>
            <li>Have your vet's emergency number ready</li>
        </ul>

        <p style="color:#dc2626; font-weight:600;">This is an AI-generated alert. Please seek professional veterinary care immediately.</p>
        """

        return self._send_email(
            from_email=user_email,
            to_email=user_email,
            subject=f"🚨 EMERGENCY: Health Alert for {dog_name}",
            html_body=_email_template(
                title=f"Emergency Health Alert — {dog_name}",
                body_html=body_html,
                footer_note="⚠️ This is an automated emergency alert. Please contact a veterinarian immediately.",
            ),
        )

    def send_health_summary_email(
        self,
        user_email: str,
        dog_name: str,
        breed: str,
        age: str,
        weight: str,
        summary: str,
        vaccine_schedule: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Send a comprehensive health summary email."""
        body_html = f"""
        <p>Here's a health summary for <strong>{dog_name}</strong>:</p>

        <div style="background:#eff6ff; border-left:4px solid #3b82f6; padding:16px 20px; border-radius:8px; margin:16px 0;">
            <p style="margin:0; font-weight:600; color:#1e40af;">🐶 Dog Profile</p>
            <table style="margin-top:8px; color:#1e3a5f;">
                <tr><td style="padding:2px 12px 2px 0; font-weight:500;">Name:</td><td>{dog_name}</td></tr>
                <tr><td style="padding:2px 12px 2px 0; font-weight:500;">Breed:</td><td>{breed}</td></tr>
                <tr><td style="padding:2px 12px 2px 0; font-weight:500;">Age:</td><td>{age} years</td></tr>
                <tr><td style="padding:2px 12px 2px 0; font-weight:500;">Weight:</td><td>{weight} kg</td></tr>
            </table>
        </div>

        <div style="margin:16px 0;">
            <p style="font-weight:600; color:#374151;">📋 Health Summary</p>
            <p style="color:#4b5563; line-height:1.8;">{summary}</p>
        </div>

        {'<div style="background:#f0fdf4; border-left:4px solid #22c55e; padding:16px 20px; border-radius:8px; margin:16px 0;"><p style="margin:0; font-weight:600; color:#166534;">💉 Vaccine Schedule</p><p style="color:#15803d; white-space:pre-line;">' + vaccine_schedule + '</p></div>' if vaccine_schedule else ''}

        <p>Stay on top of {dog_name}'s health with regular check-ups! 🐾</p>
        """

        return self._send_email(
            from_email=user_email,
            to_email=user_email,
            subject=f"📋 Health Summary for {dog_name} — K9 Care",
            html_body=_email_template(
                title=f"Health Summary — {dog_name}",
                body_html=body_html,
            ),
        )
