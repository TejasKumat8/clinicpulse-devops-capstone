def test_health_returns_up(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_ready_checks_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "READY"}


def test_root_describes_service(client):
    body = client.get("/").json()
    assert body["service"] == "ClinicPulse API"
    assert body["author"] == "Tejas Kumat"
    assert body["docs"] == "/docs"


def test_info_exposes_build_sha(client):
    body = client.get("/api/info").json()
    assert set(body) == {"service", "version", "gitSha", "environment"}


def test_metrics_endpoint_is_prometheus_format(client):
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "http_requests_total" in response.text
    assert "clinicpulse_appointments_booked_total" in response.text
