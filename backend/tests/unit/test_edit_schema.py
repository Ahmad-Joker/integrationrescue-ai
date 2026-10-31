"""Edit validation: mixed-up fields get a specific, actionable error instead of a vague policy rejection or crash.

Found in the first live Gemini eval: the model put json_set values in ``new`` and sent replace edits without
``old``; one of those crashed the orchestrator with a TypeError.
"""

import pytest
from pydantic import ValidationError

from integrationrescue.agent.tools import Edit, PatchProposal
from integrationrescue.security.policy import review_patch

GOOD_SET = {"op": "json_set", "path": "tenants/a.json", "key_path": ["price_plan_map", "p"], "value": "pro"}
GOOD_REPLACE = {"op": "replace", "path": "sync/handler.py", "old": "a", "new": "b"}


def test_well_formed_edits_validate():
    PatchProposal(edits=[GOOD_SET, GOOD_REPLACE], rationale="r")


@pytest.mark.parametrize(("edit", "msg"), [
    ({**GOOD_SET, "value": None, "new": "pro"}, "not old/new"),
    ({**GOOD_SET, "value": None}, "non-null value"),
    ({**GOOD_SET, "key_path": []}, "non-empty key_path"),
    ({"op": "replace", "path": "sync/handler.py", "value": "whole file"}, "not key_path/value"),
    ({"op": "replace", "path": "sync/handler.py", "new": "x"}, "non-empty 'old'"),
])
def test_mixed_up_fields_are_rejected_with_actionable_message(edit, msg):
    with pytest.raises(ValidationError, match=msg):
        Edit(**edit)


def test_policy_rejects_malformed_replace_instead_of_crashing(tmp_path):
    r = review_patch(tmp_path, [{"op": "replace", "path": "sync/handler.py", "old": None, "new": "x"}])
    assert not r.allowed and "replace requires" in r.findings[0]
