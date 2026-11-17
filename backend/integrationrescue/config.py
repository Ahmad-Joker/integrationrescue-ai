"""Runtime settings from environment variables, validated once at startup.

Local development needs no configuration. A public competition demo (``IR_DEMO_MODE=1``) must be configured
explicitly: the app refuses to start rather than run exposed with a missing access code or a malformed value.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from urllib.parse import urlparse

PROVIDERS = {"deterministic", "heuristic", "baseline", "heuristic-baseline", "gemini", "google", "claude", "anthropic"}
DEV_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")
MIN_TOKEN_LEN = 16


class ConfigError(ValueError):
    pass


def _flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int, lo: int, hi: int, errors: list[str]) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        errors.append(f"{name} must be an integer")
        return default
    if not lo <= value <= hi:
        errors.append(f"{name} must be between {lo} and {hi}")
    return value


@dataclass(frozen=True)
class Settings:
    demo_mode: bool = False
    access_token: str = ""
    admin_token: str = ""
    cors_origins: tuple[str, ...] = DEV_ORIGINS
    default_provider: str = "deterministic"
    rate_limit_per_min: int = 30
    max_concurrent_runs: int = 3
    max_live_incidents_per_day: int = 15
    trust_proxy: bool = False
    static_dir: str = ""
    warnings: list[str] = field(default_factory=list)

    @property
    def access_required(self) -> bool:
        return bool(self.access_token)

    def public(self) -> dict[str, object]:
        """What the dashboard may know about the configuration (never a token)."""
        return {"demo_mode": self.demo_mode, "access_required": self.access_required,
                "default_provider": self.default_provider, "auto_approve_allowed": not self.demo_mode,
                "eval_run_allowed": not self.demo_mode, "max_live_incidents_per_day": self.max_live_incidents_per_day}


def load_settings() -> Settings:
    errors: list[str] = []
    warnings: list[str] = []
    demo = _flag("IR_DEMO_MODE")
    token = os.environ.get("IR_ACCESS_TOKEN", "").strip()
    admin = os.environ.get("IR_ADMIN_TOKEN", "").strip()
    for name, value in (("IR_ACCESS_TOKEN", token), ("IR_ADMIN_TOKEN", admin)):
        if value and len(value) < MIN_TOKEN_LEN:
            errors.append(f"{name} must be at least {MIN_TOKEN_LEN} characters")
    if demo and not token:
        errors.append("IR_DEMO_MODE=1 requires IR_ACCESS_TOKEN (the access code judges enter)")
    if token and admin and token == admin:
        errors.append("IR_ADMIN_TOKEN must differ from IR_ACCESS_TOKEN")

    origins = DEV_ORIGINS
    raw_origins = os.environ.get("IR_CORS_ORIGINS", "").strip()
    if raw_origins:
        origins = tuple(o.strip().rstrip("/") for o in raw_origins.split(",") if o.strip())
        for o in origins:
            u = urlparse(o)
            if o == "*" or u.scheme not in {"http", "https"} or not u.netloc or u.path:
                errors.append(f"IR_CORS_ORIGINS entry {o!r} must be an exact origin like https://demo.example.com")

    provider = os.environ.get("IR_PROVIDER", "deterministic").strip().lower() or "deterministic"
    if provider not in PROVIDERS:
        errors.append(f"IR_PROVIDER must be one of {sorted(PROVIDERS)}")
    if provider in {"gemini", "google"} and not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        warnings.append("IR_PROVIDER is gemini but GEMINI_API_KEY is not set; live runs will be refused")
    _int("IR_MAX_LLM_CALLS", 30, 1, 200, errors)

    static_dir = os.environ.get("IR_STATIC_DIR", "").strip()
    if static_dir and not os.path.isdir(static_dir):
        errors.append(f"IR_STATIC_DIR {static_dir!r} is not a directory (build the frontend first)")

    settings = Settings(
        demo_mode=demo, access_token=token, admin_token=admin, cors_origins=origins, default_provider=provider,
        rate_limit_per_min=_int("IR_RATE_LIMIT_PER_MIN", 30, 1, 10_000, errors),
        max_concurrent_runs=_int("IR_MAX_CONCURRENT_RUNS", 3, 1, 50, errors),
        max_live_incidents_per_day=_int("IR_MAX_LIVE_INCIDENTS_PER_DAY", 15, 0, 10_000, errors),
        trust_proxy=_flag("IR_TRUST_PROXY"), static_dir=static_dir, warnings=warnings,
    )
    if errors:
        raise ConfigError("invalid configuration: " + "; ".join(errors))
    return settings
