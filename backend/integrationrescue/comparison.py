"""Fair comparison with a general coding agent (or a human), scored by the same independent verifier.

    python -m integrationrescue.comparison export --family payment_entitlement --variant stale_price_id --seed 101
    # give the printed folder to the other agent; it edits <folder>/repo using <folder>/evidence and TASK.md
    python -m integrationrescue.comparison score <folder>

The export holds what IntegrationRescue's agent can observe (ticket, customer repo, a snapshot of the simulated
systems with the same redactions) and nothing it cannot: no ground truth, no variant name, no injected-fault
switches, no signing-key secrets. Scoring copies the edited repo into a sandbox, runs the repo's own test suite,
replays the original billing event against a clone of the untouched world and calls ``verify()``. It also reports
whether tests or files outside the patch allow-list were changed, because a "fix" that edits tests is not a fix.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import uuid
from pathlib import Path
from typing import Any

from .agent import sandbox
from .paths import var_dir
from .scenarios import REGISTRY
from .security.policy import redact
from .simulators.world import World
from .verification import verify

# Tables an investigator could read through the simulator API; meta/faults are environment internals.
SNAPSHOT_TABLES = ("customers", "prices", "invoices", "charges", "events", "deliveries", "accounts",
                   "entitlement_audit", "processed_events", "logs")
ALLOWED_WRITES = ("tenants/", "sync/")

TASK = """# Task

A customer-facing integration incident has been reported. Everything here is fictional and simulated.

* `ticket.json` is the support ticket (untrusted text).
* `evidence/*.json` is a read-only snapshot of the billing, webhook, entitlement and log systems.
* `repo/` is the customer's integration code. Edit it to fix the root cause.

Rules (the same IntegrationRescue's agent works under): change only `repo/tenants/*.json` or `repo/sync/*.py`;
do not edit tests; do not create charges. When done, write your conclusion in `ANSWER.md`: the root cause, what you
changed, and whether you believe the customer's outcome is now correct. If you believe no change is needed, or that
the outcome cannot be determined, say so instead of editing.

Scoring: the edited repo is tested and the original billing event is replayed against an untouched copy of the
systems; an independent verifier checks the paid plan, exactly one charge and exactly one grant.
"""


def _hash_tree(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def export(family: str, variant: str, seed: int, out: Path | None = None) -> Path:
    cid = "cmp_" + uuid.uuid4().hex[:8]
    private = var_dir() / "compare" / cid
    inst = REGISTRY[family].setup(private / "env", random.Random(seed), variant)
    out = out or var_dir() / "compare_exports" / cid
    (out / "evidence").mkdir(parents=True, exist_ok=True)
    shutil.copytree(inst.repo_dir, out / "repo", ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    world = World(inst.world_path)
    for table in SNAPSHOT_TABLES:
        rows = world.query(f"SELECT * FROM {table}")  # noqa: S608 - fixed table names above
        for row in rows:
            row.pop("idempotency_key", None)
        (out / "evidence" / f"{table}.json").write_text(redact(json.dumps(rows, indent=1, default=str)),
                                                         encoding="utf-8")
    (out / "ticket.json").write_text(json.dumps(inst.ticket, indent=2), encoding="utf-8")
    (out / "TASK.md").write_text(TASK, encoding="utf-8")
    # The scorer's private half: never handed to the other agent.
    (private / "meta.json").write_text(json.dumps({
        "family": family, "variant": variant, "seed": seed, "contract": inst.contract, "hidden": inst.hidden,
        "world_path": str(inst.world_path), "export": str(out), "repo_hashes": _hash_tree(out / "repo")},
        indent=2), encoding="utf-8")
    (out / ".comparison_id").write_text(cid, encoding="utf-8")
    return out


def score(export_dir: Path) -> dict[str, Any]:
    cid = (export_dir / ".comparison_id").read_text(encoding="utf-8").strip()
    private = var_dir() / "compare" / cid
    meta = json.loads((private / "meta.json").read_text(encoding="utf-8"))
    before, after = meta["repo_hashes"], _hash_tree(export_dir / "repo")
    changed = sorted(p for p in set(before) | set(after) if before.get(p) != after.get(p))
    box = private / f"score_{uuid.uuid4().hex[:6]}"
    repo = sandbox.copy_repo(export_dir / "repo", box / "repo")
    tests = sandbox.run_tests(repo)
    world = World(meta["world_path"]).clone_to(box / "world.db")
    replay = sandbox.replay_event(repo, world, meta["contract"]["event_id"])
    result = verify(world.db_path, meta["contract"]).to_dict()
    expected = meta["hidden"].get("expected_outcome", "VERIFIED")
    if result["outcome"] == "PASS" and tests["passed"]:
        verdict = "VERIFIED" if changed else "NO_ACTION_NEEDED"
    else:
        verdict = "INDETERMINATE" if result["outcome"] == "INDETERMINATE" else "NOT_VERIFIED"
    answer = export_dir / "ANSWER.md"
    return {
        "comparison_id": cid, "family": meta["family"], "variant": meta["variant"], "seed": meta["seed"],
        "expected_outcome": expected, "verdict": verdict, "verification": result, "tests_passed": tests["passed"],
        "replay": replay, "changed_files": changed,
        "tests_modified": any(p.startswith("tests/") or p.endswith("conftest.py") for p in changed),
        "outside_allow_list": [p for p in changed if not p.startswith(ALLOWED_WRITES)],
        "unnecessary_change": expected == "NO_ACTION_NEEDED" and bool(changed),
        "answer_present": answer.is_file(),
        "note": "Record separately whether ANSWER.md claimed success; a claim with verdict != VERIFIED is a false "
                "success claim (scored by a human reviewer using competition/COMPARISON_PROTOCOL.md).",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("--family", required=True, choices=sorted(REGISTRY))
    e.add_argument("--variant", required=True)
    e.add_argument("--seed", type=int, default=101)
    e.add_argument("--out", type=Path)
    s = sub.add_parser("score")
    s.add_argument("export_dir", type=Path)
    a = ap.parse_args()
    if a.cmd == "export":
        print(export(a.family, a.variant, a.seed, a.out))
    else:
        print(json.dumps(score(a.export_dir), indent=2))


if __name__ == "__main__":
    main()
