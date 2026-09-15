"""
Google OAuth2 authentication service.
Handles OAuth flow, token storage (PostgreSQL), and credential refresh.
Google Calendar & Gmail APIs are free for personal use.
"""
import logging
import json
from datetime import datetime, timezone
from typing import Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

from config import Config

logger = logging.getLogger(__name__)


class GoogleAuthService:
    """Manages Google OAuth2 authentication for Calendar and Gmail access."""

    def __init__(self):
        self._client_config = {
            "web": {
                "client_id": Config.GOOGLE_CLIENT_ID,
                "client_secret": Config.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [Config.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

    def is_configured(self) -> bool:
        """Check if Google OAuth credentials are configured."""
        return bool(
            Config.GOOGLE_CLIENT_ID
            and Config.GOOGLE_CLIENT_ID != "your_google_client_id_here"
            and Config.GOOGLE_CLIENT_SECRET
            and Config.GOOGLE_CLIENT_SECRET != "your_google_client_secret_here"
        )

    def get_authorization_url(self) -> Optional[str]:
        """Generate the Google OAuth2 authorization URL."""
        if not self.is_configured():
            logger.warning("Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.")
            return None

        try:
            flow = Flow.from_client_config(
                self._client_config,
                scopes=Config.GOOGLE_SCOPES,
                redirect_uri=Config.GOOGLE_REDIRECT_URI,
            )
            auth_url, _ = flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
                prompt="consent",
            )
            return auth_url
        except Exception as e:
            logger.error(f"Failed to generate authorization URL: {e}")
            return None

    def handle_callback(self, authorization_code: str) -> Optional[dict]:
        """
        Exchange authorization code for tokens and store them.
        Returns user info dict on success, None on failure.
        """
        if not self.is_configured():
            return None

        try:
            flow = Flow.from_client_config(
                self._client_config,
                scopes=Config.GOOGLE_SCOPES,
                redirect_uri=Config.GOOGLE_REDIRECT_URI,
            )
            flow.fetch_token(code=authorization_code)
            credentials = flow.credentials

            # Get user email
            from googleapiclient.discovery import build
            service = build("oauth2", "v2", credentials=credentials)
            user_info = service.userinfo().get().execute()
            email = user_info.get("email", "")

            # Store tokens in database
            self._store_token(
                email=email,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_uri=credentials.token_uri,
                scopes=json.dumps(list(credentials.scopes)) if credentials.scopes else None,
                expiry=credentials.expiry,
            )

            logger.info(f"Google OAuth completed for {email}")
            return {
                "email": email,
                "name": user_info.get("name", ""),
                "picture": user_info.get("picture", ""),
            }

        except Exception as e:
            logger.error(f"OAuth callback failed: {e}")
            return None

    def get_credentials(self, email: str) -> Optional[Credentials]:
        """Get valid Google credentials for a given email. Refreshes if expired."""
        token_data = self._load_token(email)
        if not token_data:
            return None

        credentials = Credentials(
            token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=Config.GOOGLE_CLIENT_ID,
            client_secret=Config.GOOGLE_CLIENT_SECRET,
            scopes=json.loads(token_data["scopes"]) if token_data.get("scopes") else Config.GOOGLE_SCOPES,
        )

        # Refresh if expired
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                self._store_token(
                    email=email,
                    access_token=credentials.token,
                    refresh_token=credentials.refresh_token,
                    token_uri=credentials.token_uri,
                    scopes=json.dumps(list(credentials.scopes)) if credentials.scopes else None,
                    expiry=credentials.expiry,
                )
                logger.info(f"Refreshed Google token for {email}")
            except Exception as e:
                logger.error(f"Failed to refresh token for {email}: {e}")
                return None

        return credentials

    def is_authenticated(self, email: str) -> bool:
        """Check if a user has valid stored credentials."""
        creds = self.get_credentials(email)
        return creds is not None and creds.valid

    def revoke_access(self, email: str) -> bool:
        """Revoke Google access and delete stored tokens."""
        try:
            from database import get_db_session, GoogleToken
            db = get_db_session()
            if db:
                token = db.query(GoogleToken).filter_by(email=email).first()
                if token:
                    db.delete(token)
                    db.commit()
                db.close()
            logger.info(f"Revoked Google access for {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke access: {e}")
            return False

    def _store_token(self, email: str, access_token: str, refresh_token: Optional[str],
                     token_uri: str, scopes: Optional[str], expiry: Optional[datetime]):
        """Store or update OAuth token in the database."""
        try:
            from database import get_db_session, GoogleToken
            db = get_db_session()
            if not db:
                logger.warning("Database not available. Token not stored.")
                return

            existing = db.query(GoogleToken).filter_by(email=email).first()
            if existing:
                existing.access_token = access_token
                if refresh_token:
                    existing.refresh_token = refresh_token
                existing.token_uri = token_uri
                existing.scopes = scopes
                existing.expiry = expiry
                existing.updated_at = datetime.now(timezone.utc)
            else:
                token = GoogleToken(
                    email=email,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_uri=token_uri,
                    scopes=scopes,
                    expiry=expiry,
                )
                db.add(token)

            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to store token: {e}")

    def _load_token(self, email: str) -> Optional[dict]:
        """Load OAuth token from the database."""
        try:
            from database import get_db_session, GoogleToken
            db = get_db_session()
            if not db:
                return None

            token = db.query(GoogleToken).filter_by(email=email).first()
            db.close()

            if not token:
                return None

            return {
                "access_token": token.access_token,
                "refresh_token": token.refresh_token,
                "token_uri": token.token_uri,
                "scopes": token.scopes,
                "expiry": token.expiry,
            }
        except Exception as e:
            logger.error(f"Failed to load token: {e}")
            return None
