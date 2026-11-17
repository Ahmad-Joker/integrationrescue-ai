"""Competition-grade access control for a publicly reachable demo.

Deliberately small: one shared access code for judges (state-changing requests), a separate admin code for resets,
a per-client sliding-window rate limit and a daily cap on live-model incidents so a public URL cannot drain the
model quota. Not a user system: there are no accounts, and the codes are rotated by redeploying.
"""

from __future__ import annotations

import hmac
import threading
import time
from collections import deque
from datetime import UTC, datetime

from starlette.requests import Request

ACCESS_HEADER = "x-access-token"
ADMIN_HEADER = "x-admin-token"


def token_ok(supplied: str | None, expected: str) -> bool:
    """Constant-time comparison; an unset expected token means the check is disabled."""
    if not expected:
        return True
    return bool(supplied) and hmac.compare_digest(supplied.encode(), expected.encode())


def client_key(request: Request, trust_proxy: bool) -> str:
    # Behind a platform proxy every request comes from the proxy, so the left-most forwarded address is the client.
    # Only trusted when configured: otherwise any caller could spoof the header to dodge the rate limit.
    if trust_proxy:
        fwd = request.headers.get("x-forwarded-for", "")
        if fwd:
            return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimiter:
    def __init__(self, per_minute: int, window_s: float = 60.0):
        self.per_minute = per_minute
        self.window_s = window_s
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        with self._lock:
            q = self._hits.setdefault(key, deque())
            while q and now - q[0] >= self.window_s:
                q.popleft()
            if len(q) >= self.per_minute:
                return False
            q.append(now)
            if len(self._hits) > 10_000:  # bound memory under a spray of addresses
                self._hits = {k: v for k, v in self._hits.items() if v}
            return True


class DailyCap:
    """Counts events per UTC day (e.g. live-model incidents); resets at midnight UTC."""

    def __init__(self, limit: int):
        self.limit = limit
        self._day = ""
        self._count = 0
        self._lock = threading.Lock()

    def take(self) -> bool:
        with self._lock:
            today = datetime.now(UTC).strftime("%Y-%m-%d")
            if today != self._day:
                self._day, self._count = today, 0
            if self._count >= self.limit:
                return False
            self._count += 1
            return True

    def remaining(self) -> int:
        with self._lock:
            today = datetime.now(UTC).strftime("%Y-%m-%d")
            return self.limit if today != self._day else max(0, self.limit - self._count)
