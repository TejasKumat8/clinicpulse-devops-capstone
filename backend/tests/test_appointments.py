from datetime import datetime, timedelta

import pytest


# ---------- POST /api/appointments ----------
def test_create_appointment(book, doctors):
    response = book()
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "SCHEDULED"
    assert body["doctor_name"] == doctors[0].name
    assert body["department"] == "CARDIOLOGY"
    assert body["appointment_type"] == "IN_PERSON"
    start = datetime.fromisoformat(body["scheduled_at"])
    assert datetime.fromisoformat(body["ends_at"]) - start == timedelta(minutes=30)


def test_create_appointment_teleconsult(book):
    response = book(appointment_type="TELECONSULT", reason="Follow-up remote video consultation")
    assert response.status_code == 201
    body = response.json()
    assert body["appointment_type"] == "TELECONSULT"
    assert body["reason"] == "Follow-up remote video consultation"


def test_double_booking_same_doctor_is_rejected(book):
    assert book().status_code == 201
    clash = book(offset_minutes=15, patient_name="Second Patient")
    assert clash.status_code == 409
    assert "already has appointment" in clash.json()["detail"]


def test_back_to_back_and_other_doctor_slots_are_allowed(book, doctors):
    assert book().status_code == 201
    # Starts exactly when first appointment ends:
    assert book(offset_minutes=30).status_code == 201
    # Same time slot, but different doctor:
    assert book(doctor=doctors[1]).status_code == 201


def test_cannot_book_in_the_past(book):
    past = (datetime.now() - timedelta(days=1)).isoformat()
    response = book(scheduled_at=past)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "overrides",
    [
        {"patient_name": " "},
        {"patient_phone": "invalid-phone"},
        {"duration_minutes": 5},
        {"duration_minutes": 240},
        {"doctor_id": 999},
        {"appointment_type": "HOME_VISIT"},
    ],
)
def test_invalid_payloads_are_rejected(book, overrides):
    assert book(**overrides).status_code == 422


# ---------- GET /api/appointments ----------
def test_list_and_filter_appointments(client, book, doctors):
    book(patient_name="Asha Verma", appointment_type="IN_PERSON")
    book(doctor=doctors[1], patient_name="Kabir Singh", appointment_type="TELECONSULT")

    assert len(client.get("/api/appointments").json()) == 2

    cardio = client.get("/api/appointments", params={"department": "CARDIOLOGY"}).json()
    assert [a["patient_name"] for a in cardio] == ["Asha Verma"]

    search = client.get("/api/appointments", params={"q": "kabir"}).json()
    assert [a["patient_name"] for a in search] == ["Kabir Singh"]

    tele = client.get("/api/appointments", params={"type": "TELECONSULT"}).json()
    assert [a["patient_name"] for a in tele] == ["Kabir Singh"]

    assert client.get("/api/appointments", params={"status": "COMPLETED"}).json() == []


def test_get_single_appointment_and_404(client, book):
    created = book().json()
    assert client.get(f"/api/appointments/{created['id']}").json()["id"] == created["id"]
    assert client.get("/api/appointments/987654").status_code == 404


# ---------- PUT /api/appointments/{id} ----------
def test_status_lifecycle(client, book):
    appointment_id = book().json()["id"]
    url = f"/api/appointments/{appointment_id}"

    assert client.put(url, json={"status": "CHECKED_IN"}).json()["status"] == "CHECKED_IN"
    assert client.put(url, json={"status": "COMPLETED"}).json()["status"] == "COMPLETED"

    # COMPLETED is terminal
    assert client.put(url, json={"status": "SCHEDULED"}).status_code == 409
    assert client.put(url, json={"duration_minutes": 45}).status_code == 409


def test_cannot_skip_check_in(client, book):
    appointment_id = book().json()["id"]
    response = client.put(f"/api/appointments/{appointment_id}", json={"status": "COMPLETED"})
    assert response.status_code == 409


def test_reschedule_checks_conflicts(client, book, tomorrow_9am):
    book()
    second = book(offset_minutes=60).json()
    url = f"/api/appointments/{second['id']}"

    clash = client.put(url, json={"scheduled_at": tomorrow_9am.isoformat()})
    assert clash.status_code == 409

    moved = client.put(url, json={"scheduled_at": (tomorrow_9am + timedelta(hours=3)).isoformat()})
    assert moved.status_code == 200
    assert moved.json()["ends_at"].startswith((tomorrow_9am + timedelta(hours=3, minutes=30)).isoformat()[:16])


def test_cancelled_slot_can_be_rebooked(client, book):
    first = book().json()
    client.put(f"/api/appointments/{first['id']}", json={"status": "CANCELLED"})
    assert book(patient_name="Walk-in Patient").status_code == 201


# ---------- DELETE /api/appointments/{id} ----------
def test_delete_appointment(client, book):
    appointment_id = book().json()["id"]
    assert client.delete(f"/api/appointments/{appointment_id}").status_code == 204
    assert client.get(f"/api/appointments/{appointment_id}").status_code == 404
    assert client.delete(f"/api/appointments/{appointment_id}").status_code == 404


# ---------- GET /api/appointments/stats ----------
def test_stats(client, book, doctors):
    a = book(appointment_type="IN_PERSON").json()
    book(doctor=doctors[1], appointment_type="TELECONSULT")
    client.put(f"/api/appointments/{a['id']}", json={"status": "CANCELLED"})

    stats = client.get("/api/appointments/stats").json()
    assert stats["total"] == 2
    assert stats["scheduled"] == 1
    assert stats["cancelled"] == 1
    assert stats["inPerson"] == 1
    assert stats["teleconsult"] == 1
    assert stats["byDepartment"] == {"CARDIOLOGY": 1, "GENERAL": 1}


def test_booking_increments_business_metric(client, book):
    book(appointment_type="TELECONSULT")
    metrics = client.get("/metrics").text
    assert 'clinicpulse_appointments_booked_total{appointment_type="TELECONSULT",department="CARDIOLOGY"}' in metrics
