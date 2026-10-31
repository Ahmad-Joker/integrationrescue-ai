"""Deterministic trust-boundary enforcement. The model never gets to override these rules."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

SECRET_PATTERNS = [
    (re.compile(r"sk_(live|test)_[A-Za-z0-9]{8,}"), "sk_***REDACTED***"),
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{12,}"), "Bearer ***REDACTED***"),
    (re.compile(r"(?i)(api[_-]?key|secret|password|token)(\"?\s*[:=]\s*\"?)[^\s\",}]{6,}"), r"\1\2***REDACTED***"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"), "gh*_***REDACTED***"),
]

READ_DENY_GLOBS = [".env", ".env.*", "*.pem", "*.key", "secrets/*", ".git/*", "*/.git/*"]
WRITE_ALLOW_GLOBS = ["tenants/*.json", "sync/*.py"]
WRITE_DENY_GLOBS = ["tests/*", "conftest.py", "*/conftest.py"]
FORBIDDEN_CODE = [r"\bimport\s+(os|subprocess|socket|shutil|ctypes|importlib)\b", r"\bfrom\s+(os|subprocess|socket)\b",
                  r"\beval\s*\(", r"\bexec\s*\(", r"__import__", r"\bopen\s*\(.*['\"]w"]
MAX_EDITS = 5
MAX_CHANGED_LINES = 40
ALLOWED_PLANS = {"free", "pro"}


class PolicyViolation(Exception):
    pass


def redact(text: str) -> str:
    for pattern, repl in SECRET_PATTERNS:
        text = pattern.sub(repl, text)
    return text


def safe_relpath(root: Path, rel: str) -> Path:
    """Resolve rel inside root or raise. Rejects absolute paths, traversal and denied files."""
    if not rel or rel.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", rel):
        raise PolicyViolation(f"absolute paths are not allowed: {rel!r}")
    posix = PurePosixPath(rel.replace("\\", "/"))
    if ".." in posix.parts:
        raise PolicyViolation(f"path traversal is not allowed: {rel!r}")
    s = str(posix)
    if any(fnmatch.fnmatch(s, g) for g in READ_DENY_GLOBS) or any(p.startswith(".") for p in posix.parts):
        raise PolicyViolation(f"access to {rel!r} is denied by policy")
    root = root.resolve()
    target = (root / s).resolve()
    if root != target and root not in target.parents:
        raise PolicyViolation(f"path escapes the workspace: {rel!r}")
    return target


def check_write_path(rel: str) -> None:
    s = rel.replace("\\", "/")
    if any(fnmatch.fnmatch(s, g) for g in WRITE_DENY_GLOBS):
        raise PolicyViolation(f"patches may not modify tests or verification code: {rel!r}")
    if not any(fnmatch.fnmatch(s, g) for g in WRITE_ALLOW_GLOBS):
        raise PolicyViolation(f"path {rel!r} is outside the patchable allow-list {WRITE_ALLOW_GLOBS}")


@dataclass
class PatchReview:
    allowed: bool
    risk: str
    findings: list[str] = field(default_factory=list)
    changed_lines: int = 0


def review_patch(repo: Path, edits: list[dict[str, Any]]) -> PatchReview:
    """Static review of a proposed patch before it touches any sandbox."""
    findings: list[str] = []
    if not edits:
        return PatchReview(False, "n/a", ["patch is empty"])
    if len(edits) > MAX_EDITS:
        return PatchReview(False, "high", [f"too many edits ({len(edits)} > {MAX_EDITS})"])
    changed = 0
    risk = "low"
    for e in edits:
        path = e.get("path", "")
        try:
            safe_relpath(repo, path)
            check_write_path(path)
        except PolicyViolation as exc:
            return PatchReview(False, "high", [str(exc)])
        op = e.get("op")
        if op == "json_set":
            if not isinstance(e.get("key_path"), list) or not e["key_path"]:
                return PatchReview(False, "high", ["json_set requires a non-empty key_path"])
            if e["key_path"][0] == "price_plan_map" and e.get("value") not in ALLOWED_PLANS:
                return PatchReview(False, "high", [f"unknown plan value {e.get('value')!r}"])
            changed += 1
        elif op == "replace":
            new = str(e.get("new", ""))
            for pat in FORBIDDEN_CODE:
                if re.search(pat, new):
                    return PatchReview(False, "high", [f"patch introduces forbidden construct /{pat}/"])
            changed += max(len(new.splitlines()), 1)
            if path.endswith(".py"):
                risk = "medium"
                findings.append(f"code change in {path} (affects all tenants)")
        else:
            return PatchReview(False, "high", [f"unsupported edit op {op!r}"])
    if changed > MAX_CHANGED_LINES:
        return PatchReview(False, "high", [f"patch too large ({changed} lines)"], changed)
    if risk == "low":
        findings.append("configuration-only change scoped to a single tenant file" if
                        len({e['path'] for e in edits}) == 1 else "configuration-only change")
    return PatchReview(True, risk, findings, changed)
