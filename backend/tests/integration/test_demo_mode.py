"""Public competition demo: access code, admin reset, limits, no auto-approval, config validation, static serving."""

import time

import pytest
from fastapi.testclient import TestClient

from integrationrescue.config import ConfigError, Settings, load_settings
from integrationrescue.security.access import DailyCap, RateLimiter

ACCESS = "judge-access-code-0001"
ADMIN = "admin-reset-code-00002"


@pytest.fixture
def demo(svc, monkeypatch, tmp_path):
    from integrationrescue import api
    static = tmp_path / "dist"
    (static / "assets").mkdir(parents=True)
    (static / "index.html").write_text("<!doctype html><title>IR</title>", encoding="utf-8")
    (static / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
    (tmp_path / "secret.txt").write_text("outside", encoding="utf-8")
    settings = Settings(demo_mode=True, access_token=ACCESS, admin_token=ADMIN, static_dir=str(static),
                        rate_limit_per_min=1000, max_live_incidents_per_day=0)
    monkeypatch.setattr(api, "SETTINGS", settings)
    monkeypatch.setattr(api, "_svc", svc)
    monkeypatch.setattr(api, "_limiter", RateLimiter(1000))
    monkeypatch.setattr(api, "_live_cap", DailyCap(0))
    return TestClient(api.app)


def _wait(client, iid, phases=("done", "awaiting_approval"), timeout=120):
    end = time.time() + timeout
    while time.time() < end:
        inc = client.get(f"/api/incidents/{iid}").json()
        if inc["phase"] in phases and not inc["running"]:
            return inc
        time.sleep(0.3)
    raise AssertionError("incident did not settle")


def test_state_changes_need_the_access_code(demo):
    health = demo.get("/api/health").json()
    assert health["demo_mode"] and health["access_required"] and not health["auto_approve_allowed"]
    assert ACCESS not in str(health) and ADMIN not in str(health)
    assert demo.post("/api/incidents", json={"autorun": False}).status_code == 401
    assert demo.post("/api/incidents", json={"autorun": False},
                     headers={"x-access-token": "wrong-code-wrong-code"}).status_code == 401
    assert demo.post("/api/access/check", headers={"x-access-token": ACCESS}).json() == {"ok": True}
    # Reads stay open: the data is fictional and judges should not need the code to look around.
    assert demo.get("/api/incidents").status_code == 200


def test_judge_flow_requires_human_approval(demo):
    h = {"x-access-token": ACCESS}
    assert demo.post("/api/incidents", json={"auto_approve": True}, headers=h).status_code == 403
    iid = demo.post("/api/incidents", json={"variant": "case_mismatch", "seed": 11}, headers=h).json()["id"]
    inc = _wait(demo, iid)
    assert inc["phase"] == "awaiting_approval" and inc["approval"] is None
    assert demo.post(f"/api/incidents/{iid}/approve", json={"approver": "judge"}).status_code == 401
    assert demo.post(f"/api/incidents/{iid}/approve", json={"approver": "judge"}, headers=h).status_code == 200
    assert _wait(demo, iid, ("done",))["outcome"] == "VERIFIED"
    assert demo.post("/api/eval/run", json={}, headers=h).status_code == 403


def test_live_model_cap_protects_quota(demo, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real")
    r = demo.post("/api/incidents", json={"provider": "gemini", "autorun": False},
                  headers={"x-access-token": ACCESS})
    assert r.status_code == 429 and "deterministic baseline is still available" in r.json()["detail"]


def test_rate_limit_and_body_size(demo, monkeypatch):
    from integrationrescue import api
    monkeypatch.setattr(api, "_limiter", RateLimiter(2))
    h = {"x-access-token": ACCESS}
    codes = [demo.post("/api/access/check", headers=h).status_code for _ in range(3)]
    assert codes == [200, 200, 429]
    big = demo.post("/api/access/check", headers={**h, "content-length": "99999999"}, content=b"x")
    assert big.status_code == 413


def test_admin_reset_reseeds_fictional_state(demo):
    h = {"x-access-token": ACCESS}
    demo.post("/api/incidents", json={"autorun": False}, headers=h)
    assert demo.post("/api/admin/reset", headers=h).status_code == 401  # access code is not the admin code
    r = demo.post("/api/admin/reset", headers={"x-admin-token": ADMIN})
    assert r.status_code == 200 and len(r.json()["seeded"]) == 2
    rows = demo.get("/api/incidents").json()
    assert {row["mode"] for row in rows} == {"deterministic"}
    phases = sorted(row["phase"] for row in rows)
    assert phases == ["awaiting_approval", "done"]  # the seeded repair waits for a human


def test_dashboard_is_served_without_path_traversal(demo):
    assert "<title>IR</title>" in demo.get("/").text
    assert demo.get("/assets/app.js").text == "console.log(1)"
    assert "<title>IR</title>" in demo.get("/some/client/route").text  # SPA fallback
    assert "outside" not in demo.get("/..%2fsecret.txt").text
    assert demo.get("/api/nope").status_code == 404
    page = demo.get("/")
    assert "frame-ancestors 'none'" in page.headers["content-security-policy"]
    assert page.headers["x-content-type-options"] == "nosniff"


def test_featured_scenarios_exist():
    from integrationrescue.demo_seed import FEATURED
    from integrationrescue.scenarios import REGISTRY
    for f in FEATURED:
        fam = REGISTRY[f["family"]]
        assert f["variant"] in fam.variants + fam.heldout_variants
        assert set(f["faults"]) <= {"duplicate_delivery", "lost_ack", "billing_ledger_unavailable"}


@pytest.mark.parametrize("env, message", [
    ({"IR_DEMO_MODE": "1"}, "requires IR_ACCESS_TOKEN"),
    ({"IR_ACCESS_TOKEN": "short"}, "at least 16"),
    ({"IR_ACCESS_TOKEN": ACCESS, "IR_ADMIN_TOKEN": ACCESS}, "must differ"),
    ({"IR_CORS_ORIGINS": "*"}, "exact origin"),
    ({"IR_CORS_ORIGINS": "https://ok.example.com,https://bad.example.com/path"}, "exact origin"),
    ({"IR_PROVIDER": "gpt"}, "IR_PROVIDER"),
    ({"IR_RATE_LIMIT_PER_MIN": "lots"}, "integer"),
    ({"IR_STATIC_DIR": "/definitely/not/here"}, "not a directory"),
])
def test_invalid_configuration_refuses_to_start(monkeypatch, env, message):
    for key in ("IR_DEMO_MODE", "IR_ACCESS_TOKEN", "IR_ADMIN_TOKEN", "IR_CORS_ORIGINS", "IR_STATIC_DIR"):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    with pytest.raises(ConfigError, match=message):
        load_settings()


def test_valid_demo_configuration(monkeypatch):
    monkeypatch.setenv("IR_DEMO_MODE", "1")
    monkeypatch.setenv("IR_ACCESS_TOKEN", ACCESS)
    monkeypatch.setenv("IR_CORS_ORIGINS", "https://demo.example.com")
    s = load_settings()
    assert s.demo_mode and s.access_required and s.cors_origins == ("https://demo.example.com",)
    assert "token" not in str(s.public()).lower() or ACCESS not in str(s.public())


def test_rate_limiter_window_and_daily_cap():
    rl = RateLimiter(2, window_s=60)
    assert rl.allow("a", 0) and rl.allow("a", 1) and not rl.allow("a", 2)
    assert rl.allow("b", 2)  # per client
    assert rl.allow("a", 61)  # window slid
    cap = DailyCap(1)
    assert cap.take() and not cap.take() and cap.remaining() == 0
