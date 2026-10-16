def test_list_doctors(client, doctors):
    response = client.get("/api/doctors")
    assert response.status_code == 200
    names = [d["name"] for d in response.json()]
    assert names == ["Dr. Test Cardio", "Dr. Test General"]  # sorted by department


def test_create_doctor(client):
    response = client.post(
        "/api/doctors",
        json={"name": "Dr. Sneha Roy", "department": "NEUROLOGY", "room": "N-302"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["department"] == "NEUROLOGY"
    assert body["active"] is True
    assert body["room"] == "N-302"


def test_duplicate_doctor_is_rejected(client, doctors):
    response = client.post(
        "/api/doctors",
        json={"name": "Dr. Test Cardio", "department": "CARDIOLOGY"},
    )
    assert response.status_code == 409


def test_doctor_department_is_validated(client):
    response = client.post(
        "/api/doctors",
        json={"name": "Dr. Nobody", "department": "ASTROLOGY"},
    )
    assert response.status_code == 422


def test_unknown_doctor_returns_404(client):
    assert client.get("/api/doctors/999").status_code == 404
