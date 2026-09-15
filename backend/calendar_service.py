"""
Google Calendar Service — creates, lists, and manages vaccine/health reminder events.
Uses the Google Calendar API v3. Free for personal use.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

from googleapiclient.discovery import build

from google_auth import GoogleAuthService

logger = logging.getLogger(__name__)


class CalendarService:
    """Manages Google Calendar events for vaccine reminders and vet appointments."""

    def __init__(self, auth_service: GoogleAuthService):
        self.auth = auth_service

    def _get_service(self, email: str):
        """Get authenticated Calendar API service for a user."""
        credentials = self.auth.get_credentials(email)
        if not credentials:
            return None
        return build("calendar", "v3", credentials=credentials)

    def create_vaccine_reminder(
        self,
        email: str,
        dog_name: str,
        vaccine_name: str,
        due_date: str,
        notes: str = "",
    ) -> Optional[Dict[str, Any]]:
        """
        Create a vaccine reminder event on Google Calendar.

        Args:
            email: User's Google email
            dog_name: Name of the dog
            vaccine_name: Name of the vaccine
            due_date: Date string in YYYY-MM-DD format
            notes: Additional notes

        Returns:
            Dict with event details on success, None on failure
        """
        service = self._get_service(email)
        if not service:
            return None

        try:
            event_body = {
                "summary": f"💉 {vaccine_name} — {dog_name}",
                "description": (
                    f"Vaccine Reminder for {dog_name}\n\n"
                    f"Vaccine: {vaccine_name}\n"
                    f"Dog: {dog_name}\n\n"
                    f"{notes}\n\n"
                    f"— Scheduled by K9 Care Chat (Dr. Paws) 🐾"
                ),
                "start": {
                    "date": due_date,
                    "timeZone": "Asia/Colombo",
                },
                "end": {
                    "date": due_date,
                    "timeZone": "Asia/Colombo",
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "email", "minutes": 1440},  # 1 day before
                        {"method": "popup", "minutes": 60},    # 1 hour before
                        {"method": "popup", "minutes": 10080}, # 1 week before
                    ],
                },
                "colorId": "9",  # Blueberry color
            }

            event = service.events().insert(calendarId="primary", body=event_body).execute()
            logger.info(f"Created calendar event '{event['summary']}' (ID: {event['id']})")

            return {
                "event_id": event["id"],
                "summary": event["summary"],
                "date": due_date,
                "link": event.get("htmlLink", ""),
            }

        except Exception as e:
            logger.error(f"Failed to create calendar event: {e}")
            return None

    def create_vet_appointment(
        self,
        email: str,
        dog_name: str,
        reason: str,
        date: str,
        time: str = "10:00",
        duration_hours: int = 1,
        vet_name: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Create a vet appointment event with specific time."""
        service = self._get_service(email)
        if not service:
            return None

        try:
            start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(hours=duration_hours)

            event_body = {
                "summary": f"🏥 Vet Visit — {dog_name}: {reason}",
                "description": (
                    f"Veterinary Appointment for {dog_name}\n\n"
                    f"Reason: {reason}\n"
                    f"{'Vet: ' + vet_name if vet_name else ''}\n\n"
                    f"— Scheduled by K9 Care Chat (Dr. Paws) 🐾"
                ),
                "start": {
                    "dateTime": start_dt.isoformat(),
                    "timeZone": "Asia/Colombo",
                },
                "end": {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": "Asia/Colombo",
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "email", "minutes": 1440},
                        {"method": "popup", "minutes": 120},
                        {"method": "popup", "minutes": 30},
                    ],
                },
                "colorId": "11",  # Tomato color for urgency
            }

            event = service.events().insert(calendarId="primary", body=event_body).execute()
            logger.info(f"Created vet appointment '{event['summary']}' (ID: {event['id']})")

            return {
                "event_id": event["id"],
                "summary": event["summary"],
                "date": date,
                "time": time,
                "link": event.get("htmlLink", ""),
            }

        except Exception as e:
            logger.error(f"Failed to create vet appointment: {e}")
            return None

    def list_upcoming_reminders(
        self,
        email: str,
        days_ahead: int = 60,
    ) -> List[Dict[str, Any]]:
        """List upcoming K9 Care related calendar events."""
        service = self._get_service(email)
        if not service:
            return []

        try:
            now = datetime.now(timezone.utc)
            time_max = now + timedelta(days=days_ahead)

            events_result = service.events().list(
                calendarId="primary",
                timeMin=now.isoformat(),
                timeMax=time_max.isoformat(),
                maxResults=20,
                singleEvents=True,
                orderBy="startTime",
                q="K9 Care Chat",  # Search for our events
            ).execute()

            events = events_result.get("items", [])
            results = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date", ""))
                results.append({
                    "event_id": event["id"],
                    "summary": event.get("summary", ""),
                    "date": start,
                    "description": event.get("description", ""),
                    "link": event.get("htmlLink", ""),
                })

            return results

        except Exception as e:
            logger.error(f"Failed to list calendar events: {e}")
            return []

    def delete_reminder(self, email: str, event_id: str) -> bool:
        """Delete a calendar event by ID."""
        service = self._get_service(email)
        if not service:
            return False

        try:
            service.events().delete(calendarId="primary", eventId=event_id).execute()
            logger.info(f"Deleted calendar event {event_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete calendar event: {e}")
            return False
