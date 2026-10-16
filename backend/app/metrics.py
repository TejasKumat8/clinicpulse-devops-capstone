"""ClinicPulse application metrics exposed on /metrics for Prometheus scraping."""

from prometheus_client import Counter

APPOINTMENTS_BOOKED = Counter(
    "clinicpulse_appointments_booked_total",
    "Appointments booked through the ClinicPulse API",
    ["department", "appointment_type"],
)

APPOINTMENT_STATUS_CHANGES = Counter(
    "clinicpulse_appointment_status_changes_total",
    "Appointment lifecycle status transitions",
    ["status"],
)

BOOKING_CONFLICTS = Counter(
    "clinicpulse_booking_conflicts_total",
    "Booking attempts rejected due to doctor schedule conflicts",
)
