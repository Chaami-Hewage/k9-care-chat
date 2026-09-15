"""
PostgreSQL database models using SQLAlchemy.
Supports multiple dogs per owner, vaccine records, and scheduled reminders.
"""
import logging
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from config import Config

logger = logging.getLogger(__name__)

Base = declarative_base()
engine = None
SessionLocal = None


def init_db():
    """Initialize the database engine and create tables."""
    global engine, SessionLocal
    try:
        engine = create_engine(Config.DATABASE_URL, pool_pre_ping=True, echo=False)
        SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.warning(f"PostgreSQL initialization failed ({e}). Falling back to SQLite...")
        try:
            import os
            db_path = os.path.join(os.path.dirname(__file__), "k9care.db")
            sqlite_url = f"sqlite:///{db_path}"
            engine = create_engine(sqlite_url, echo=False)
            SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
            Base.metadata.create_all(bind=engine)
            logger.info("SQLite Database initialized successfully.")
        except Exception as sqle:
            logger.error(f"Failed to initialize SQLite fallback: {sqle}")
            logger.warning("Database features will be unavailable.")


def get_db():
    """Get a database session. Returns None if DB is not initialized."""
    if SessionLocal is None:
        return None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """Get a single database session (non-generator). Caller must close it."""
    if SessionLocal is None:
        return None
    return SessionLocal()


# ──────────────────────────────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────────────────────────────

class Dog(Base):
    """A dog profile belonging to an owner."""
    __tablename__ = "dogs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    breed = Column(String(100), nullable=False, default="Unknown Breed")
    age_years = Column(Float, nullable=False, default=1.0)
    weight_kg = Column(Float, nullable=False, default=10.0)
    owner_email = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    vaccine_records = relationship("VaccineRecord", back_populates="dog", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="dog", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "breed": self.breed,
            "age_years": self.age_years,
            "weight_kg": self.weight_kg,
            "owner_email": self.owner_email,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class VaccineRecord(Base):
    """Record of a vaccine that has been administered to a dog."""
    __tablename__ = "vaccine_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dog_id = Column(Integer, ForeignKey("dogs.id", ondelete="CASCADE"), nullable=False)
    vaccine_name = Column(String(100), nullable=False)
    date_administered = Column(DateTime, nullable=False)
    next_due_date = Column(DateTime, nullable=True)
    administered_by = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    dog = relationship("Dog", back_populates="vaccine_records")

    def to_dict(self):
        return {
            "id": self.id,
            "dog_id": self.dog_id,
            "vaccine_name": self.vaccine_name,
            "date_administered": self.date_administered.isoformat() if self.date_administered else None,
            "next_due_date": self.next_due_date.isoformat() if self.next_due_date else None,
            "administered_by": self.administered_by,
            "notes": self.notes,
        }


class Reminder(Base):
    """A scheduled reminder (linked to Google Calendar event)."""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dog_id = Column(Integer, ForeignKey("dogs.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=False)
    reminder_type = Column(String(50), default="vaccine")  # vaccine, checkup, medication, other
    google_event_id = Column(String(255), nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    dog = relationship("Dog", back_populates="reminders")

    def to_dict(self):
        return {
            "id": self.id,
            "dog_id": self.dog_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "reminder_type": self.reminder_type,
            "google_event_id": self.google_event_id,
            "is_completed": self.is_completed,
        }


class GoogleToken(Base):
    """Stores Google OAuth2 tokens per user/email."""
    __tablename__ = "google_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_uri = Column(String(500), default="https://oauth2.googleapis.com/token")
    scopes = Column(Text, nullable=True)
    expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "has_refresh_token": bool(self.refresh_token),
            "expiry": self.expiry.isoformat() if self.expiry else None,
        }
