#!/usr/bin/env python3
"""Seed ClinicPulse with realistic clinical demo appointments via the REST API.

Usage:
    python scripts/seed_demo_data.py                       # Local Docker Compose (http://localhost:3000)
    python scripts/seed_demo_data.py http://clinicpulse.local # Kubernetes Ingress URL
"""

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000").rstrip("/")

PATIENTS = [
    ("Aarav Mehta", "+91 98201 11223", "Chest tightness during cardio workout", "IN_PERSON", "Bring previous ECG"),
    ("Sneha Deshmukh", "+91 98202 22334", "Child immunization — 12 month measles vaccine", "IN_PERSON", "Check booster card"),
    ("Vikram Choudhary", "+91 98203 33445", "Persistent dry cough and mild fever", "IN_PERSON", "Prescribe syrup if needed"),
    ("Ananya Sen", "+91 98204 44556", "Chronic lower back stiffness and sciatica", "IN_PERSON", "X-ray requested"),
    ("Rohan Kulkarni", "+91 98205 55667", "Dermatology review — eczema flare up", "TELECONSULT", "Patient on travel"),
    ("Meera Nambiar", "+91 98206 66778", "Migraine headaches occurring alternate days", "TELECONSULT", "Review MRI scan"),
    ("Kavita Iyer", "+91 98207 77889", "Hypertension medication review", "TELECONSULT", "Check daily BP logs"),
    ("Aditya Birla", "+91 98208 88990", "Follow-up post knee arthroscopy", "IN_PERSON", "Physical therapy assessment"),
    ("Pooja Nair", "+91 98209 99001", "Severe sore throat and swallowing difficulty", "IN_PERSON", "Swab test recommended"),
    ("Rajesh Bhatt", "+91 98210 10203", "Periodic vertigo and imbalance", "TELECONSULT", "ENT consult advised"),
    ("Tanvi Joshi", "+91 98211 21314", "Pediatric wellness examination", "IN_PERSON", "Growth chart tracking"),
    ("Suresh Reddy", "+91 98212 32425", "Lipid profile and cholesterol review", "TELECONSULT", "Fasting report attached"),
]


def call(method: str, path: str, body: dict | None = None):
    req = urllib.request.Request(
        f"{BASE}/api{path}",
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        raw = response.read()
        return json.loads(raw) if raw else None


def main() -> None:
    print(f"Connecting to ClinicPulse at {BASE}...")
    try:
        doctors = call("GET", "/doctors")
    except Exception as exc:
        sys.exit(f"Failed to fetch doctors: {exc}. Ensure the backend is running and migrated.")

    if not doctors:
        sys.exit("No doctors found in the database. Run alembic upgrade head.")

    print(f"Found {len(doctors)} active doctors.")
    start = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

    booked = []
    for i, (name, phone, reason, appt_type, notes) in enumerate(PATIENTS):
        doctor = doctors[i % len(doctors)]
        slot = start + timedelta(days=i // 6, minutes=45 * (i % 6))
        payload = {
            "patient_name": name,
            "patient_phone": phone,
            "doctor_id": doctor["id"],
            "scheduled_at": slot.strftime("%Y-%m-%dT%H:%M:00"),
            "duration_minutes": 30,
            "reason": reason,
            "appointment_type": appt_type,
            "notes": notes,
        }
        try:
            appt = call("POST", "/appointments", payload)
            booked.append(appt)
            print(f"  [+] Booked: {name} -> {doctor['name']} ({doctor['department']}) [{appt_type}]")
        except urllib.error.HTTPError as exc:
            err = exc.read().decode()
            print(f"  [!] Skipped {name}: {err}")

    # Advance a few appointments along the visit lifecycle
    if len(booked) >= 4:
        call("PUT", f"/appointments/{booked[0]['id']}", {"status": "CHECKED_IN"})
        call("PUT", f"/appointments/{booked[0]['id']}", {"status": "COMPLETED"})
        print(f"  [✓] Advanced appointment #{booked[0]['id']} -> COMPLETED")

        call("PUT", f"/appointments/{booked[1]['id']}", {"status": "CHECKED_IN"})
        print(f"  [✓] Advanced appointment #{booked[1]['id']} -> CHECKED_IN")

        call("PUT", f"/appointments/{booked[2]['id']}", {"status": "CANCELLED"})
        print(f"  [✓] Advanced appointment #{booked[2]['id']} -> CANCELLED")

    stats = call("GET", "/appointments/stats")
    print("\nClinicPulse Data Summary:")
    print(f"  Total Appointments: {stats.get('total')}")
    print(f"  Scheduled: {stats.get('scheduled')}")
    print(f"  Checked In: {stats.get('checkedIn')}")
    print(f"  Completed: {stats.get('completed')}")
    print(f"  In-Person: {stats.get('inPerson')}")
    print(f"  Teleconsult: {stats.get('teleconsult')}")
    print("Done! Refresh the dashboard at " + BASE)


if __name__ == "__main__":
    main()
