import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"ok": True}


def test_client_and_account_flow():
    c = client.post("/api/clients", json={"name": "Acme Co"}).json()
    a = client.post(f"/api/clients/{c['id']}/accounts", json={"platform": "Google Ads"}).json()
    assert a["status"] == "not_started"

    updated = client.patch(f"/api/accounts/{a['id']}", json={"status": "live"}).json()
    assert updated["status"] == "live"

    assert client.patch(f"/api/accounts/{a['id']}", json={"status": "bogus"}).status_code == 422
    assert client.get("/api/stats").json()["live"] >= 1

    assert client.delete(f"/api/clients/{c['id']}").status_code == 204


def test_missing_client_404():
    assert client.post("/api/clients/99999/accounts", json={"platform": "X"}).status_code == 404
