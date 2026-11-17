"""Customer code runs with an allow-listed environment and, on POSIX, kernel resource limits."""

import os
import subprocess
import sys

import pytest

from integrationrescue.security.child import child_env, limited


def test_child_env_drops_secrets(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "should-not-leak")
    monkeypatch.setenv("IR_ACCESS_TOKEN", "should-not-leak-either")
    env = child_env()
    assert "GEMINI_API_KEY" not in env and "IR_ACCESS_TOKEN" not in env
    assert set(k.upper() for k in env) <= {"SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "TEMP", "TMP", "PATH", "LANG",
                                           "LC_ALL"}


@pytest.mark.skipif(os.name != "posix", reason="rlimits exist only on POSIX; Windows relies on the wall-clock timeout")
def test_limits_are_applied_on_posix():
    probe = ("import resource;"
             "print(resource.getrlimit(resource.RLIMIT_CPU)[0], resource.getrlimit(resource.RLIMIT_NOFILE)[0],"
             " resource.getrlimit(resource.RLIMIT_AS)[0])")
    out = subprocess.run(limited([sys.executable, "-I", "-c", probe], cpu_s=7, mem_mb=512),
                         capture_output=True, text=True, timeout=30, env=child_env())
    assert out.returncode == 0, out.stderr
    cpu, nofile, mem = map(int, out.stdout.split())
    assert cpu == 7 and nofile <= 256 and mem == 512 * 1024 * 1024


@pytest.mark.skipif(os.name != "posix", reason="rlimits exist only on POSIX")
def test_cpu_hog_is_killed_on_posix():
    out = subprocess.run(limited([sys.executable, "-I", "-c", "while True: pass"], cpu_s=1),
                         capture_output=True, text=True, timeout=30, env=child_env())
    assert out.returncode != 0  # SIGXCPU/SIGKILL from the kernel, long before the 30 s wall clock


def test_windows_and_other_platforms_keep_the_command():
    if os.name != "posix":
        assert limited(["x"], 5) == ["x"]
    else:
        assert limited(["x"], 5)[-1] == "x"
