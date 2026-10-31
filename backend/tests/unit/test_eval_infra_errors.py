from integrationrescue import evaluation
from integrationrescue.agent import orchestrator
from integrationrescue.agent.providers import Provider, ProviderError


class QuotaProvider(Provider):
    name = "gemini"
    mode = "live"

    def next_actions(self, view):
        raise ProviderError("model quota exhausted for test-model (resets in ~300 min)")


def test_quota_errors_are_reported_not_scored_and_stop_the_suite(monkeypatch):
    monkeypatch.setattr(orchestrator, "make_provider", lambda kind=None: QuotaProvider())
    res = evaluation.run_suite("gemini", seeds=[1], families=["payment_entitlement"])
    s = res["summary"]
    assert len(res["rows"]) == 1 and res["rows"][0]["infra_error"].startswith("model quota exhausted")
    assert s["runs"] == 0 and s["infra_errors"] == 1 and s["stopped_early"]
    assert s["correct_diagnosis_rate"] == 0 and s["by_family"] == {}
