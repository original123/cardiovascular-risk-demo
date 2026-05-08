from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_evaluate_endpoint_success():
    response = client.post(
        "/api/risk/evaluate",
        json={
            "sex": 1,
            "age": 40,
            "region": 1,
            "area": 1,
            "waist": 90,
            "tc_unit": 1,
            "tc": 200,
            "hdlc_unit": 1,
            "hdlc": 40,
            "sbp": 120,
            "dbp": 80,
            "drug": 0,
            "dm": 0,
            "csmoke": 0,
            "fh_ascvd": 0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["result"]["tenYearRisk"]["percent"] == 1.1
    assert data["result"]["models"]["lifetimeRisk"]["type"] == "black_box_poly2_approximation"


def test_evaluate_endpoint_validation_error():
    response = client.post("/api/risk/evaluate", json={"sex": 1})
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert "评测项不得为空" in data["message"]


def test_evaluate_endpoint_hides_lifetime_for_age_sixty():
    payload = {
        "sex": 1,
        "age": 60,
        "region": 1,
        "area": 1,
        "waist": 90,
        "tc_unit": 1,
        "tc": 200,
        "hdlc_unit": 1,
        "hdlc": 40,
        "sbp": 120,
        "dbp": 80,
        "drug": 0,
        "dm": 0,
        "csmoke": 0,
        "fh_ascvd": 0,
    }
    response = client.post("/api/risk/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()["result"]
    assert data["lifetimeRisk"] is None
    assert data["idealLifetimeRisk"] is None
