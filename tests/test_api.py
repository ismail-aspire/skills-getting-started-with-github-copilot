import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient
from app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect some known activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    test_email = "teststudent@example.com"

    # Ensure not already signed up
    resp = client.get("/activities")
    assert resp.status_code == 200
    before = resp.json()
    initial_count = len(before[activity]["participants"])

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Confirm added
    resp = client.get("/activities")
    after = resp.json()
    assert test_email in after[activity]["participants"]
    assert len(after[activity]["participants"]) == initial_count + 1

    # Unregister
    resp = client.delete(f"/activities/{activity}/participants?email={test_email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Confirm removed
    resp = client.get("/activities")
    final = resp.json()
    assert test_email not in final[activity]["participants"]
    assert len(final[activity]["participants"]) == initial_count
