"""A model outage or quota error must never look like a success or like an agent decision."""

import pytest

from integrationrescue.agent.providers import HeuristicProvider, Provider, ProviderError


class _Failing(Provider):
    name, mode = "fake-live", "live"

    def __init__(self, message: str, fail_in: str = "investigate"):
        self.message, self.fail_in, self.inner = message, fail_in, HeuristicProvider()

    def next_actions(self, view):
        if view.phase == self.fail_in:
            raise ProviderError(self.message)
        return self.inner.next_actions(view)

    def observe(self, results):
        self.inner.observe(results)


@pytest.mark.parametrize("message, kind", [
    ("model quota exhausted for gemini-x (resets in ~300 min)", "infrastructure"),
    ("model call failed: HTTP 503: overloaded", "infrastructure"),
    ("model call budget exhausted (30)", "budget"),
    ("model declined the request (SAFETY)", "model"),
])
def test_provider_failure_is_recorded_and_never_verified(svc, message, kind):
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", 5)
    inc = svc.run(iid, provider=_Failing(message))
    assert inc["phase"] == "done"
    assert inc["outcome"] == "ESCALATED"  # no diagnosis was reached
    assert inc["data"]["provider_error"] == {"kind": kind, "message": message}
    assert inc["data"]["verification"].get("outcome") != "PASS"


def test_failure_after_diagnosis_reports_diagnosed_not_verified(svc):
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", 6)
    inc = svc.run(iid, provider=_Failing("model call failed: ReadTimeout", fail_in="patch"))
    assert inc["data"]["diagnosis"] is not None
    assert inc["outcome"] == "DIAGNOSED" and inc["data"]["provider_error"]["kind"] == "infrastructure"
    assert inc["data"]["patch"] is None
