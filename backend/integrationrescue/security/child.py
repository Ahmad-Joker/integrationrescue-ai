"""How customer code is launched: an allow-listed environment and, on POSIX, kernel resource limits.

This is process hardening, not a sandbox: the child can still read files the service user can read. The container
image runs as an unprivileged user with only the fictional state directory writable; real customer code would need
OS isolation (gVisor/Firecracker/containers per run) - see docs/LIMITATIONS.md.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Only what an interpreter needs to start; API keys and every other variable stay in the parent.
SAFE_ENV_KEYS = {"SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "TEMP", "TMP", "PATH", "LANG", "LC_ALL"}
TRAMPOLINE = Path(__file__).resolve().parent / "rlimit_exec.py"
DEFAULT_MEM_MB = 2048


def child_env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if k.upper() in SAFE_ENV_KEYS}


def limited(cmd: list[str], cpu_s: int, mem_mb: int = DEFAULT_MEM_MB) -> list[str]:
    """Wrap ``cmd`` so it runs under CPU, memory, file-size and open-file limits (POSIX only).

    A small exec trampoline sets the limits, because ``preexec_fn`` is unsafe in a threaded server. Windows has no
    rlimits; there the wall-clock timeout of the caller is the only bound.
    """
    if os.name != "posix":
        return cmd
    return [sys.executable, "-I", str(TRAMPOLINE), str(cpu_s), str(mem_mb), "--", *cmd]
