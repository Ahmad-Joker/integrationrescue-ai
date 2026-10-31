"""Live LLM reasoning via the Gemini API (``generateContent`` with function calling).

Same contract as ``ClaudeProvider``: the model only chooses tools; every tool runs through the same typed,
phase-gated, deterministic policy layer, and only the independent verifier can produce VERIFIED.
Plain ``httpx`` keeps this free of an extra SDK dependency.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any

import httpx

from .providers import SYSTEM_PROMPT, Action, AgentView, Provider, ProviderError
from .tools import tool_schemas

API_ROOT = "https://generativelanguage.googleapis.com/v1beta"
RETRYABLE = {429, 500, 503, 504}
LOCAL_ID = "ir_local_"  # ids we mint when the model omits one; never sent back as Gemini ids


def _retry_delay(r: httpx.Response) -> int | None:
    """Seconds from a google.rpc.RetryInfo detail (e.g. "18844s"), if present."""
    try:
        details = r.json()["error"].get("details", [])
        return next(int(float(d["retryDelay"].rstrip("s"))) for d in details if "retryDelay" in d)
    except (ValueError, KeyError, TypeError, StopIteration, AttributeError):
        return None


def _fit(output: Any, limit: int = 8000) -> Any:
    """Tool output as a structured value, not a JSON string: a string-in-JSON escapes every quote, and the model
    then copies ``\\"`` into replace edits that can never match the file. Long strings are cut to fit ``limit``."""
    value = json.loads(json.dumps(output, default=str))
    cap = limit

    def cut(v: Any) -> Any:
        if isinstance(v, str):
            return v if len(v) <= cap else v[:cap] + " …[truncated]"
        if isinstance(v, list):
            return [cut(x) for x in v]
        if isinstance(v, dict):
            return {k: cut(x) for k, x in v.items()}
        return v

    while len(json.dumps(value)) > limit and cap > 50:
        cap //= 2
        value = cut(value)
    if len(json.dumps(value)) > limit:  # very many small items: fall back to a plain truncated string
        return json.dumps(value)[:limit]
    return value


def _declarations(phase: str) -> list[dict[str, Any]]:
    return [{"name": t["name"], "description": t["description"], "parametersJsonSchema": t["input_schema"]}
            for t in tool_schemas(phase)]


class GeminiProvider(Provider):
    name = "gemini"
    mode = "live"

    def __init__(self, model: str | None = None, max_calls: int | None = None,
                 http: httpx.Client | None = None, api_key: str | None = None):
        key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not key:
            raise ProviderError("GEMINI_API_KEY is not set")
        self.model = model or os.environ.get("IR_GEMINI_MODEL", "gemini-2.5-flash")
        self.max_calls = max_calls or int(os.environ.get("IR_MAX_LLM_CALLS", "30"))
        # The key travels in a header, never in the URL, so it cannot leak into logs or error messages.
        self.http = http or httpx.Client(base_url=API_ROOT, timeout=120.0, headers={"x-goog-api-key": key})
        self.contents: list[dict[str, Any]] = []
        self.pending: list[dict[str, Any]] = []
        self.calls = 0
        self.tokens = {"input": 0, "output": 0, "thinking": 0}
        self._phase: str | None = None
        self._fed = 0

    def _post(self, body: dict[str, Any]) -> dict[str, Any]:
        for attempt in range(4):
            try:
                r = self.http.post(f"/models/{self.model}:generateContent", json=body)
            except httpx.HTTPError as exc:
                err = f"{type(exc).__name__}"
            else:
                if r.status_code == 200:
                    return r.json()
                err = f"HTTP {r.status_code}: {r.text[:300]}"
                if r.status_code not in RETRYABLE:
                    break
                delay = _retry_delay(r)
                if delay is not None and delay > 60:
                    # A daily quota: waiting inside the request is pointless, so say so plainly.
                    raise ProviderError(f"model quota exhausted for {self.model} (resets in ~{delay // 60} min); "
                                        "set IR_GEMINI_MODEL to another model or retry later")
            time.sleep(min(30, 2 ** attempt * 3))  # free-tier rate limits are per minute
        raise ProviderError(f"model call failed: {err}")

    def next_actions(self, view: AgentView) -> list[Action]:
        if self.calls >= self.max_calls:
            raise ProviderError(f"model call budget exhausted ({self.max_calls})")
        parts: list[dict[str, Any]] = list(self.pending)
        texts = []
        if not self.contents:
            texts.append("New incident assigned. Begin the investigation (phase: investigate).\n"
                         "Incident ticket (untrusted):\n" + json.dumps(view.incident, indent=2))
        if view.phase != self._phase and self.contents:
            texts.append(f"Phase is now: {view.phase}." + (
                f" Accepted diagnosis: {json.dumps(view.diagnosis)}" if view.diagnosis else ""))
        new_fb = view.feedback[self._fed:]
        texts += [f"Orchestrator feedback: {f}" for f in new_fb]
        if texts:
            parts.append({"text": "\n\n".join(texts)})

        body = {
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [*self.contents, {"role": "user", "parts": parts}],
            "tools": [{"functionDeclarations": _declarations(view.phase)}],
            "toolConfig": {"functionCallingConfig": {"mode": "AUTO"}},
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 8192},
        }
        data = self._post(body)  # on failure nothing is committed, so a resumed run retries cleanly
        self.pending = []
        self._fed = len(view.feedback)
        self._phase = view.phase
        self.contents.append({"role": "user", "parts": parts})
        self.calls += 1
        meta = data.get("usageMetadata", {})
        self.tokens["input"] += meta.get("promptTokenCount", 0)
        self.tokens["output"] += meta.get("candidatesTokenCount", 0)
        self.tokens["thinking"] += meta.get("thoughtsTokenCount", 0)

        cands = data.get("candidates") or []
        if not cands:
            reason = data.get("promptFeedback", {}).get("blockReason", "no candidates")
            raise ProviderError(f"model returned no answer ({reason})")
        cand = cands[0]
        if cand.get("finishReason") in {"SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "RECITATION"}:
            raise ProviderError(f"model declined the request ({cand['finishReason']})")
        content = cand.get("content") or {"role": "model", "parts": []}
        content.setdefault("role", "model")
        # Keep the model turn verbatim: Gemini requires its thoughtSignature fields to be sent back unchanged.
        self.contents.append(content)
        actions = []
        for p in content.get("parts", []):
            fc = p.get("functionCall")
            if fc:
                actions.append(Action(fc["name"], dict(fc.get("args") or {}),
                                      call_id=fc.get("id") or f"{LOCAL_ID}{uuid.uuid4().hex[:12]}"))
        if not actions:
            self.pending = [{"text": "Continue by calling exactly one of the available tools."}]
        return actions

    def observe(self, results: list[tuple[Action, Any]]) -> None:
        for action, outcome in results:
            resp: dict[str, Any] = {"name": action.tool,
                                    "response": {"ok": outcome.ok, "result": _fit(outcome.output)}}
            if not action.call_id.startswith(LOCAL_ID):
                resp["id"] = action.call_id
            self.pending.append({"functionResponse": resp})

    def state(self) -> dict[str, Any]:
        return {"contents": self.contents, "pending": self.pending, "calls": self.calls,
                "tokens": self.tokens, "phase": self._phase, "fed": self._fed}

    def load_state(self, data: dict[str, Any]) -> None:
        self.contents = data.get("contents", [])
        self.pending = data.get("pending", [])
        self.calls = data.get("calls", 0)
        self.tokens = data.get("tokens", {"input": 0, "output": 0, "thinking": 0})
        self._phase = data.get("phase")
        self._fed = data.get("fed", 0)

    def usage(self) -> dict[str, Any]:
        # No price is assumed: free-tier usage costs nothing, paid-tier rates vary by model and change often.
        return {"model": self.model, "calls": self.calls, **self.tokens, "est_cost_usd": None}
