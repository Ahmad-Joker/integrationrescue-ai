"""Exec trampoline: apply resource limits, then replace this process with the real command (POSIX only).

usage: python -I rlimit_exec.py <cpu_seconds> <memory_mb> -- <command...>
"""

import os
import resource
import sys


def main() -> None:
    cpu, mem_mb = int(sys.argv[1]), int(sys.argv[2])
    if sys.argv[3] != "--" or len(sys.argv) < 5:
        sys.exit("usage: rlimit_exec.py CPU MEM_MB -- CMD...")
    cmd = sys.argv[4:]
    mem = mem_mb * 1024 * 1024
    for limit, value in ((resource.RLIMIT_CPU, cpu), (resource.RLIMIT_AS, mem),
                         (resource.RLIMIT_FSIZE, 64 * 1024 * 1024), (resource.RLIMIT_NOFILE, 256),
                         (resource.RLIMIT_CORE, 0)):
        _soft, hard = resource.getrlimit(limit)
        # Never try to raise a hard limit the parent already lowered (that would fail without privileges).
        value = value if hard == resource.RLIM_INFINITY else min(value, hard)
        resource.setrlimit(limit, (value, value))
    os.execv(cmd[0], cmd)


if __name__ == "__main__":
    main()
