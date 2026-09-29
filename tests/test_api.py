import pytest
from fastapi.testclient import TestClient

from app.config import META_FILE, MODEL_FILE, MONTHLY_FILE
from app.main import app

pytestmark = pytest.mark.skipif(
    not MONTHLY_FILE.exists(), reason="Run `python -m ml.prepare_data` first"
)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:  # triggers startup / DB seeding
        yield c


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_range_and_summary(client):
    rng = client.get("/api/analytics/range").json()
    assert rng["min_year"] <= rng["max_year"] and rng["states"]
    s = client.get("/api/analytics/summary").json()
    assert s["total_incidents"] > 0


def test_trend_and_by_state(client):
    state = client.get("/api/analytics/range").json()["states"][0]
    assert client.get("/api/analytics/trend", params={"state": state}).json()
    top = client.get("/api/analytics/by-state", params={"limit": 3}).json()
    assert len(top) <= 3 and top == sorted(top, key=lambda x: -x["total"])


@pytest.mark.skipif(not (MODEL_FILE.exists() and META_FILE.exists()), reason="Run `python -m ml.train` first")
def test_forecast(client):
    r = client.get("/api/predictions/forecast", params={"state": "ALL", "horizon": 6})
    assert r.status_code == 200
    body = r.json()
    assert len(body["forecast"]) == 6
    assert all(p["lower"] <= p["predicted"] <= p["upper"] for p in body["forecast"])
    assert client.get("/api/predictions/forecast", params={"state": "Atlantis"}).status_code == 404
    assert client.get("/api/predictions/model-info").status_code == 200
