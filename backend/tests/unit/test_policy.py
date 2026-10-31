import pytest

from integrationrescue.security.policy import PolicyViolation, redact, review_patch, safe_relpath


@pytest.mark.parametrize("bad", ["../secret.txt", "..\\x", "/etc/passwd", "C:\\Windows\\win.ini", ".env",
                                 "sub/.env", ".git/config", "secrets/key.txt", "id.pem", ""])
def test_rejects_unsafe_paths(tmp_path, bad):
    with pytest.raises(PolicyViolation):
        safe_relpath(tmp_path, bad)


def test_accepts_normal_path(tmp_path):
    assert safe_relpath(tmp_path, "tenants/a.json") == (tmp_path / "tenants" / "a.json").resolve()


def test_patch_cannot_touch_tests_or_unlisted_files(tmp_path):
    for path in ["tests/test_handler.py", "conftest.py", "README.md", "../outside.json"]:
        r = review_patch(tmp_path, [{"op": "replace", "path": path, "old": "a", "new": "b"}])
        assert not r.allowed, path


def test_patch_rejects_dangerous_code(tmp_path):
    r = review_patch(tmp_path, [{"op": "replace", "path": "sync/handler.py", "old": "x",
                                 "new": "import subprocess; subprocess.run('calc')"}])
    assert not r.allowed


def test_patch_rejects_unknown_plan(tmp_path):
    r = review_patch(tmp_path, [{"op": "json_set", "path": "tenants/a.json",
                                 "key_path": ["price_plan_map", "p"], "value": "enterprise_unlimited"}])
    assert not r.allowed


def test_low_risk_config_patch_allowed(tmp_path):
    r = review_patch(tmp_path, [{"op": "json_set", "path": "tenants/a.json",
                                 "key_path": ["price_plan_map", "p"], "value": "pro"}])
    assert r.allowed and r.risk == "low"


def test_too_many_edits_rejected(tmp_path):
    edit = {"op": "json_set", "path": "tenants/a.json", "key_path": ["k"], "value": 1}
    assert not review_patch(tmp_path, [edit] * 6).allowed


def test_redaction():
    text = 'token=abcdef123456 key sk_live_ABCDEFGH1234 Authorization: Bearer eyJhbGciOiJIUzI1NiJ9xx'
    out = redact(text)
    assert "abcdef123456" not in out and "sk_live_ABCDEFGH1234" not in out and "eyJhbGci" not in out
