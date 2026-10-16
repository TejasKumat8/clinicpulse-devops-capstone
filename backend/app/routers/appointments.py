from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..metrics import APPOINTMENT_STATUS_CHANGES, APPOINTMENTS_BOOKED, BOOKING_CONFLICTS
from ..models import Appointment, Doctor
from ..schemas import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentType,
    AppointmentUpdate,
    Department,
    StatsOut,
    Status,
)
from ..services import BookingConflict, can_transition, end_time, ensure_slot_free

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


def clinic_now() -> datetime:
    return datetime.now(ZoneInfo(settings.clinic_timezone)).replace(tzinfo=None)


def _get_or_404(db: Session, appointment_id: int) -> Appointment:
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


def _active_doctor_or_422(db: Session, doctor_id: int) -> Doctor:
    doctor = db.get(Doctor, doctor_id)
    if not doctor or not doctor.active:
        raise HTTPException(status_code=422, detail="Doctor does not exist or is inactive")
    return doctor


def _check_slot(db: Session, doctor_id: int, start: datetime, minutes: int, exclude_id: int | None = None) -> None:
    try:
        ensure_slot_free(db, doctor_id, start, minutes, exclude_id)
    except BookingConflict as exc:
        BOOKING_CONFLICTS.inc()
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("", response_model=list[AppointmentOut])
def list_appointments(
    db: Session = Depends(get_db),
    status_filter: Status | None = Query(default=None, alias="status"),
    doctor_id: int | None = None,
    department: Department | None = None,
    appointment_type: AppointmentType | None = Query(default=None, alias="type"),
    on: date | None = Query(default=None, description="Only appointments on this date (YYYY-MM-DD)"),
    q: str | None = Query(default=None, max_length=120, description="Search by patient name"),
    limit: int = Query(default=200, ge=1, le=500),
):
    """List appointments with filtering by status, doctor, department, consultation mode, date, or name."""
    stmt = select(Appointment).join(Appointment.doctor)
    if status_filter:
        stmt = stmt.where(Appointment.status == status_filter)
    if doctor_id:
        stmt = stmt.where(Appointment.doctor_id == doctor_id)
    if department:
        stmt = stmt.where(Doctor.department == department)
    if appointment_type:
        stmt = stmt.where(Appointment.appointment_type == appointment_type)
    if on:
        start = datetime.combine(on, time.min)
        stmt = stmt.where(Appointment.scheduled_at >= start, Appointment.scheduled_at < start + timedelta(days=1))
    if q:
        stmt = stmt.where(func.lower(Appointment.patient_name).contains(q.strip().lower()))
    stmt = stmt.order_by(Appointment.scheduled_at, Appointment.id).limit(limit)
    return list(db.scalars(stmt).unique())


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    """Retrieve operational KPIs, visit statuses, consultation types, and department breakdowns."""
    by_status = dict(
        db.execute(select(Appointment.status, func.count(Appointment.id)).group_by(Appointment.status)).all()
    )
    by_type = dict(
        db.execute(
            select(Appointment.appointment_type, func.count(Appointment.id)).group_by(Appointment.appointment_type)
        ).all()
    )
    by_department = dict(
        db.execute(
            select(Doctor.department, func.count(Appointment.id)).join(Appointment.doctor).group_by(Doctor.department)
        ).all()
    )
    today_start = datetime.combine(clinic_now().date(), time.min)
    today = db.scalar(
        select(func.count(Appointment.id)).where(
            Appointment.scheduled_at >= today_start,
            Appointment.scheduled_at < today_start + timedelta(days=1),
            Appointment.status != "CANCELLED",
        )
    )
    return StatsOut(
        total=sum(by_status.values()),
        today=today or 0,
        scheduled=by_status.get("SCHEDULED", 0),
        checkedIn=by_status.get("CHECKED_IN", 0),
        completed=by_status.get("COMPLETED", 0),
        cancelled=by_status.get("CANCELLED", 0),
        noShow=by_status.get("NO_SHOW", 0),
        inPerson=by_type.get("IN_PERSON", 0),
        teleconsult=by_type.get("TELECONSULT", 0),
        byDepartment=by_department,
    )


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Fetch an appointment by ID."""
    return _get_or_404(db, appointment_id)


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    """Book a new appointment with slot conflict detection and doctor schedule validation."""
    doctor = _active_doctor_or_422(db, payload.doctor_id)
    if payload.scheduled_at < clinic_now():
        raise HTTPException(status_code=422, detail="Appointments cannot be booked in the past")
    _check_slot(db, payload.doctor_id, payload.scheduled_at, payload.duration_minutes)

    appointment = Appointment(
        **payload.model_dump(),
        ends_at=end_time(payload.scheduled_at, payload.duration_minutes),
        status="SCHEDULED",
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    APPOINTMENTS_BOOKED.labels(
        department=doctor.department,
        appointment_type=payload.appointment_type,
    ).inc()
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(appointment_id: int, payload: AppointmentUpdate, db: Session = Depends(get_db)):
    """Update appointment details, reschedule, or progress through visit lifecycle."""
    appointment = _get_or_404(db, appointment_id)
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)

    if appointment.status == "COMPLETED" and changes.keys() - {"status", "reason", "notes"}:
        raise HTTPException(status_code=409, detail="Completed appointments can no longer be modified")

    new_status = changes.get("status", appointment.status)
    if not can_transition(appointment.status, new_status):
        raise HTTPException(
            status_code=409, detail=f"Cannot move appointment from {appointment.status} to {new_status}"
        )

    if "doctor_id" in changes:
        _active_doctor_or_422(db, changes["doctor_id"])

    doctor_id = changes.get("doctor_id", appointment.doctor_id)
    start = changes.get("scheduled_at", appointment.scheduled_at)
    minutes = changes.get("duration_minutes", appointment.duration_minutes)
    slot_changed = {"doctor_id", "scheduled_at", "duration_minutes"} & changes.keys()
    reactivated = appointment.status not in ("SCHEDULED", "CHECKED_IN") and new_status == "SCHEDULED"
    if (slot_changed or reactivated) and new_status in ("SCHEDULED", "CHECKED_IN"):
        _check_slot(db, doctor_id, start, minutes, exclude_id=appointment.id)

    old_status = appointment.status
    for key, value in changes.items():
        setattr(appointment, key, value)
    appointment.ends_at = end_time(start, minutes)
    db.commit()
    db.refresh(appointment)
    if new_status != old_status:
        APPOINTMENT_STATUS_CHANGES.labels(status=new_status).inc()
    return appointment


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Cancel and remove an appointment record."""
    appointment = _get_or_404(db, appointment_id)
    db.delete(appointment)
    db.commit()
