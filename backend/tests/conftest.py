"""Pytest test fixtures with strict database isolation.

Tests execute against an in-memory SQLite database using StaticPool, preventing any test
pollution or reliance on production PostgreSQL instances.
"""

import os
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import Doctor

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")

if TEST_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
else:
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)

TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def doctors(db_session):
    roster = [
        Doctor(name="Dr. Test Cardio", department="CARDIOLOGY", room="C-1"),
        Doctor(name="Dr. Test General", department="GENERAL", room="G-1"),
    ]
    db_session.add_all(roster)
    db_session.commit()
    return roster


@pytest.fixture()
def tomorrow_9am() -> datetime:
    return (datetime.now() + timedelta(days=2)).replace(hour=9, minute=0, second=0, microsecond=0)


@pytest.fixture()
def book(client, doctors, tomorrow_9am):
    """Factory fixture for booking appointments via REST API."""

    def _book(offset_minutes: int = 0, doctor=None, **overrides):
        payload = {
            "patient_name": "Rohan Gupta",
            "patient_phone": "+91 98765 43210",
            "doctor_id": (doctor or doctors[0]).id,
            "scheduled_at": (tomorrow_9am + timedelta(minutes=offset_minutes)).isoformat(),
            "duration_minutes": 30,
            "reason": "Routine clinical consultation",
            "appointment_type": "IN_PERSON",
            "notes": "Patient reports mild seasonal allergy",
        }
        payload.update(overrides)
        return client.post("/api/appointments", json=payload)

    return _book
