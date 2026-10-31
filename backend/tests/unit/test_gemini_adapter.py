"""Protocol tests for GeminiProvider against a fake generateContent server (no network, no quota).

The fake checks the Gemini invariants we rely on (user/model alternation, every functionCall answered by a
functionResponse with the same name and id, thoughtSignature echoed back unchanged, key sent as a header)
and answers by replaying the baseline's decisions through the real orchestrator.
"""

import itertools
import json

import httpx
import pytest

from integrationrescue.agent.gemini import API_ROOT, GeminiProvider
from integrationrescue.agent.providers import AgentView, HeuristicProvider, ProviderError


class FakeGemini:
    def __init__(self, ref, fail_first: int = 0, status: int = 503):
        self.ids = itertools.count(1)
        self.baseline = HeuristicProvider()
        self.ref = ref
        self.bodies: list[dict] = []
        self.fail_first = fail_first
        self.status = status

    def __call__(self, request: httpx.Request) -> httpx.Response:
        assert request.headers["x-goog-api-key"] == "test-key" and "key=" not in str(request.url)
        assert request.url.path.endswith("/models/gemini-3.5-flash:generateContent")
        if self.fail_first:
            self.fail_first -= 1
            return httpx.Response(self.status, json={"error": {"message": "busy"}})
        body = json.loads(request.content)
        self.bodies.append(body)
        contents = body["contents"]
        assert [c["role"] for c in contents] == ["user", "model"] * (len(contents) // 2) + ["user"]
        for prev, nxt in zip(contents, contents[1:], strict=False):
            if prev["role"] == "model":
                calls = [(p["functionCall"]["name"], p["functionCall"]["id"]) for p in prev["parts"]
                         if "functionCall" in p]
                answers = [(p["functionResponse"]["name"], p["functionResponse"].get("id")) for p in nxt["parts"]
                           if "functionResponse" in p]
                assert calls == answers
                assert all(p.get("thoughtSignature") == "sig" for p in prev["parts"] if "functionCall" in p)
        names = {d["name"] for d in body["tools"][0]["functionDeclarations"]}
        inc = self.ref["svc"].store.get(self.ref["iid"])
        d = inc["data"]
        act = self.baseline.next_actions(AgentView(inc["phase"], d["ticket"], d["trace"], d["feedback"],
                                                   d["diagnosis"]))[0]
        assert act.tool in names  # only phase-appropriate tools are offered
        part = {"functionCall": {"name": act.tool, "args": act.args, "id": f"call_{next(self.ids)}"},
                "thoughtSignature": "sig"}
        return httpx.Response(200, json={
            "candidates": [{"content": {"role": "model", "parts": [part]}, "finishReason": "STOP"}],
            "usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 20, "thoughtsTokenCount": 5}})


def _provider(fake, monkeypatch):
    monkeypatch.setattr("integrationrescue.agent.gemini.time.sleep", lambda s: None)
    http = httpx.Client(base_url=API_ROOT, transport=httpx.MockTransport(fake),
                        headers={"x-goog-api-key": "test-key"})
    return GeminiProvider(model="gemini-3.5-flash", http=http, api_key="test-key")


def test_gemini_adapter_drives_full_incident(svc, monkeypatch):
    ref = {"svc": svc}
    fake = FakeGemini(ref, fail_first=1)  # one transient 503 is retried transparently
    prov = _provider(fake, monkeypatch)
    ref["iid"] = iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=41, auto_approve=True)
    inc = svc.run(iid, provider=prov)
    assert inc["outcome"] == "VERIFIED"
    usage = prov.usage()
    assert usage["calls"] == len(fake.bodies) > 5 and usage["est_cost_usd"] is None
    texts = [p["text"] for b in fake.bodies for c in b["contents"] for p in c["parts"] if "text" in p]
    assert any("untrusted" in t for t in texts) and any("Phase is now: patch" in t for t in texts)


def test_gemini_state_round_trips_for_resume(svc, monkeypatch):
    ref = {"svc": svc}
    fake = FakeGemini(ref)
    prov = _provider(fake, monkeypatch)
    ref["iid"] = iid = svc.create_from_scenario("payment_entitlement", "case_mismatch", seed=42, auto_approve=True)
    svc.run(iid, provider=prov, max_steps=4)
    resumed = _provider(fake, monkeypatch)
    resumed.load_state(svc.store.get(iid)["data"]["provider_state"])
    assert svc.run(iid, provider=resumed)["outcome"] == "VERIFIED"


def test_gemini_non_retryable_error_is_reported_without_leaking_key(monkeypatch):
    fake = FakeGemini({}, fail_first=1, status=400)
    prov = _provider(fake, monkeypatch)
    with pytest.raises(ProviderError) as exc:
        prov.next_actions(AgentView("investigate", {"title": "t"}, [], []))
    assert "HTTP 400" in str(exc.value) and "test-key" not in str(exc.value)
    assert prov.contents == [] and prov.calls == 0  # nothing committed, so a retry starts clean


def test_missing_key_is_a_provider_error(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(ProviderError):
        GeminiProvider()


def test_daily_quota_fails_fast_with_clear_message(monkeypatch):
    sleeps = []
    monkeypatch.setattr("integrationrescue.agent.gemini.time.sleep", sleeps.append)

    def quota(request):
        return httpx.Response(429, json={"error": {"code": 429, "details": [{"retryDelay": "18844s"}]}})

    http = httpx.Client(base_url=API_ROOT, transport=httpx.MockTransport(quota))
    prov = GeminiProvider(model="gemini-3.5-flash", http=http, api_key="test-key")
    with pytest.raises(ProviderError, match="quota exhausted"):
        prov.next_actions(AgentView("investigate", {"title": "t"}, [], []))
    assert sleeps == []


def test_tool_output_is_structured_so_quotes_are_not_escaped():
    from integrationrescue.agent.gemini import _fit
    src = 'plan = resolve_plan(line["price_id"], cfg)'
    assert _fit({"path": "sync/handler.py", "content": src})["content"] == src
    big = _fit({"content": "x" * 50_000, "items": list(range(10))})
    assert len(json.dumps(big)) <= 8000 and big["content"].endswith("[truncated]") and big["items"] == list(range(10))
