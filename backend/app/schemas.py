from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Department = Literal["GENERAL", "CARDIOLOGY", "DERMATOLOGY", "PEDIATRICS", "ORTHOPEDICS", "NEUROLOGY"]
Status = Literal["SCHEDULED", "CHECKED_IN", "COMPLETED", "CANCELLED", "NO_SHOW"]
AppointmentType = Literal["IN_PERSON", "TELECONSULT"]

PHONE_PATTERN = r"^\+?[0-9][0-9 \-]{6,18}$"


def _to_wall_clock(value: datetime) -> datetime:
    """Appointments are stored in clinic wall-clock time; strip any timezone offset."""
    return value.replace(tzinfo=None, second=0, microsecond=0)


# ---------- Doctors ----------
class DoctorCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    department: Department
    room: str = Field(default="", max_length=20)


class DoctorOut(DoctorCreate):
    id: int
    active: bool
    model_config = ConfigDict(from_attributes=True)


# ---------- Appointments ----------
class AppointmentCreate(BaseModel):
    patient_name: str = Field(min_length=2, max_length=120)
    patient_phone: str = Field(pattern=PHONE_PATTERN)
    doctor_id: int = Field(gt=0)
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=10, le=120)
    reason: str = Field(default="", max_length=1000)
    appointment_type: AppointmentType = Field(default="IN_PERSON")
    notes: str = Field(default="", max_length=1000)

    @field_validator("patient_name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("patient_name must contain at least 2 non-space characters")
        return value

    @field_validator("scheduled_at")
    @classmethod
    def normalise_time(cls, value: datetime) -> datetime:
        return _to_wall_clock(value)


class AppointmentUpdate(BaseModel):
    """Partial update: only non-null fields provided in payload are altered."""

    patient_name: str | None = Field(default=None, min_length=2, max_length=120)
    patient_phone: str | None = Field(default=None, pattern=PHONE_PATTERN)
    doctor_id: int | None = Field(default=None, gt=0)
    scheduled_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, ge=10, le=120)
    reason: str | None = Field(default=None, max_length=1000)
    appointment_type: AppointmentType | None = None
    notes: str | None = Field(default=None, max_length=1000)
    status: Status | None = None

    @field_validator("scheduled_at")
    @classmethod
    def normalise_time(cls, value: datetime | None) -> datetime | None:
        return _to_wall_clock(value) if value else value


class AppointmentOut(BaseModel):
    id: int
    patient_name: str
    patient_phone: str
    doctor_id: int
    doctor_name: str
    department: str
    scheduled_at: datetime
    ends_at: datetime
    duration_minutes: int
    reason: str
    appointment_type: AppointmentType
    notes: str
    status: Status
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class StatsOut(BaseModel):
    total: int
    today: int
    scheduled: int
    checkedIn: int
    completed: int
    cancelled: int
    noShow: int
    inPerson: int
    teleconsult: int
    byDepartment: dict[str, int]


class InfoOut(BaseModel):
    service: str
    version: str
    gitSha: str
    environment: str
