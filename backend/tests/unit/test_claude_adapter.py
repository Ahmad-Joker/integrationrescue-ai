"""Protocol test for ClaudeProvider against a fake Messages client (no network, no credits).

The fake checks the Messages API invariants (alternation, every tool_use answered by a
tool_result with the same id) and answers by replaying the baseline's decisions, so the
adapter is exercised end-to-end through the real orchestrator.
"""

import itertools
from types import SimpleNamespace

from integrationrescue.agent import providers
from integrationrescue.agent.providers import AgentView, ClaudeProvider, HeuristicProvider


class Block(SimpleNamespace):
    def model_dump(self, exclude_none=True):
        return {k: v for k, v in vars(self).items() if v is not None}


class FakeMessages:
    def __init__(self, svc_ref):
        self.ids = itertools.count(1)
        self.baseline = HeuristicProvider()
        self.svc_ref = svc_ref
        self.calls = []

    def create(self, **kw):
        msgs = kw["messages"]
        self.calls.append(kw)
        assert [m["role"] for m in msgs] == ["user", "assistant"] * (len(msgs) // 2) + ["user"]
        for prev, nxt in zip(msgs, msgs[1:], strict=False):
            if prev["role"] == "assistant":
                uses = {b["id"] for b in prev["content"] if b["type"] == "tool_use"}
                results = {b["tool_use_id"] for b in nxt["content"] if b["type"] == "tool_result"}
                assert uses == results
        assert "tool_choice" not in kw and kw["model"] == "claude-opus-5-5"
        inc = self.svc_ref["svc"].store.get(self.svc_ref["iid"])
        d = inc["data"]
        phase = inc["phase"]
        view = AgentView(phase, d["ticket"], d["trace"], d["feedback"], d["diagnosis"])
        act = self.baseline.next_actions(view)[0]
        block = Block(type="tool_use", id=f"toolu_{next(self.ids)}", name=act.tool, input=act.args)
        return SimpleNamespace(content=[block], stop_reason="tool_use",
                               usage=SimpleNamespace(input_tokens=100, output_tokens=20))


def test_claude_adapter_drives_full_incident(svc, monkeypatch):
    ref = {"svc": svc}
    fake = FakeMessages(ref)

    class FakeAnthropic:
        APIError = Exception

        def Anthropic(self, **kw):  # noqa: N802 - mimics SDK constructor
            return SimpleNamespace(messages=fake)

    monkeypatch.setattr(providers, "ClaudeProvider", ClaudeProvider)
    import sys
    monkeypatch.setitem(sys.modules, "anthropic", FakeAnthropic())
    prov = ClaudeProvider()
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=31, auto_approve=True)
    ref["iid"] = iid
    inc = svc.run(iid, provider=prov)
    assert inc["outcome"] == "VERIFIED"
    assert prov.usage()["calls"] == len(fake.calls) > 5
    # Phase change was announced to the model, and the ticket was framed as untrusted.
    texts = [b["text"] for c in fake.calls for m in c["messages"] for b in m["content"] if b.get("type") == "text"]
    assert any("untrusted" in t for t in texts) and any("Phase is now: patch" in t for t in texts)
