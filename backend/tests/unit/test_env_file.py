import os
import subprocess
import sys

from integrationrescue.paths import load_env_file
from integrationrescue.simulators.sync_service import _child_env


def test_env_file_loads_without_overriding(tmp_path, monkeypatch):
    monkeypatch.delenv("IR_SKIP_DOTENV")
    monkeypatch.setenv("IR_MODEL", "from-real-env")
    monkeypatch.delenv("IR_TEST_KEY", raising=False)
    f = tmp_path / ".env"
    f.write_text("# comment\nIR_TEST_KEY='abc'  # trailing\nIR_MODEL=from-file\nEMPTY=\n", encoding="utf-8")
    assert load_env_file(f) == ["IR_TEST_KEY"]
    assert os.environ["IR_TEST_KEY"] == "abc"
    assert os.environ["IR_MODEL"] == "from-real-env"
    monkeypatch.delenv("IR_TEST_KEY")


def test_skip_flag_disables_loading(tmp_path):
    f = tmp_path / ".env"
    f.write_text("IR_TEST_KEY=abc\n", encoding="utf-8")
    assert load_env_file(f) == []


def test_api_key_never_reaches_customer_code(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-real")
    env = _child_env()
    assert "ANTHROPIC_API_KEY" not in env
    out = subprocess.run([sys.executable, "-I", "-c", "import os;print(os.environ.get('ANTHROPIC_API_KEY'))"],
                         env=env, capture_output=True, text=True).stdout.strip()
    assert out == "None"
