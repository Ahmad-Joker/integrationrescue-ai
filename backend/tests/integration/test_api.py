import time

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(svc, monkeypatch):
    from integrationrescue import api
    monkeypatch.setattr(api, "_svc", svc)
    return TestClient(api.app)


def _wait(client, iid, phases=("done", "awaiting_approval"), timeout=120):
    end = time.time() + timeout
    while time.time() < end:
        inc = client.get(f"/api/incidents/{iid}").json()
        if inc["phase"] in phases and not inc["running"]:
            return inc
        time.sleep(0.3)
    raise AssertionError("incident did not settle")


def test_full_flow_through_api(client):
    assert client.get("/api/health").json()["status"] == "ok"
    iid = client.post("/api/incidents", json={"variant": "case_mismatch", "seed": 3}).json()["id"]
    inc = _wait(client, iid)
    assert inc["phase"] == "awaiting_approval" and inc["patch"]["diff"]
    up = client.post(f"/api/incidents/{iid}/evidence",
                     files={"file": ("app.log", b"ERROR token=supersecretvalue1 checkout ok", "text/plain")})
    assert up.status_code == 200 and "supersecretvalue1" not in up.json()["text"]
    assert client.post(f"/api/incidents/{iid}/approve", json={"approver": "qa@example"}).status_code == 200
    inc = _wait(client, iid, ("done",))
    assert inc["outcome"] == "VERIFIED"
    assert "Independent verification" in client.get(f"/api/incidents/{iid}/report.md").text
    stats = client.get("/api/stats").json()
    assert stats["outcomes"]["VERIFIED"] == 1
    # Simulator endpoints are reachable for inspection.
    cid = inc["report"]["verification"]["assertions"]
    assert cid


def test_rejects_bad_requests(client):
    assert client.post("/api/incidents", json={"family": "nope"}).status_code == 400
    assert client.post("/api/incidents", json={"faults": {"rm_rf": True}}).status_code == 400
    iid = client.post("/api/incidents", json={"autorun": False}).json()["id"]
    bad = client.post(f"/api/incidents/{iid}/evidence", files={"file": ("x.exe", b"MZ", "application/octet-stream")})
    assert bad.status_code == 400
    assert client.post(f"/api/incidents/{iid}/approve", json={"approver": "x"}).status_code == 409
