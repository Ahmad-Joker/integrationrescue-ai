from integrationrescue.simulators.world import World
from integrationrescue.verification import verify


def _setup(tmp_path):
    w = World(tmp_path / "w.db")
    w.add_price("price_pro", "pro", 2900)
    ids = w.create_customer("acme", "a@acme.example", "A")
    pay = w.pay(ids["customer_id"], "price_pro", "k")
    contract = {"kind": "paid_invoice_grants_plan", "customer_id": ids["customer_id"],
                "invoice_id": pay["invoice_id"], "event_id": pay["event_id"]}
    return w, contract


def test_fails_when_entitlement_not_granted(tmp_path):
    w, contract = _setup(tmp_path)
    r = verify(w.db_path, contract)
    assert r.outcome == "FAIL"
    failed = {a.name for a in r.assertions if not a.passed}
    assert "entitlement_matches_paid_plan" in failed


def test_passes_when_granted_once(tmp_path):
    w, contract = _setup(tmp_path)
    w.set_plan(contract["customer_id"], "pro", contract["event_id"])
    assert verify(w.db_path, contract).outcome == "PASS"


def test_detects_duplicate_charge(tmp_path):
    w, contract = _setup(tmp_path)
    w.set_plan(contract["customer_id"], "pro", contract["event_id"])
    with w.conn() as c:
        c.execute("INSERT INTO charges VALUES('ch_dup', ?, 2900, 'succeeded', 'k2', 'now')", (contract["invoice_id"],))
    r = verify(w.db_path, contract)
    assert r.outcome == "FAIL"
    assert any(a.name == "exactly_one_successful_charge" and not a.passed for a in r.assertions)


def test_detects_duplicate_entitlement_side_effect(tmp_path):
    w, contract = _setup(tmp_path)
    w.set_plan(contract["customer_id"], "pro", contract["event_id"])
    w.set_plan(contract["customer_id"], "pro", contract["event_id"])
    assert verify(w.db_path, contract).outcome == "FAIL"


def test_indeterminate_when_ledger_unavailable(tmp_path):
    w, contract = _setup(tmp_path)
    w.set_plan(contract["customer_id"], "pro", contract["event_id"])
    w.set_fault("billing_ledger_unavailable")
    assert verify(w.db_path, contract).outcome == "INDETERMINATE"


def test_indeterminate_when_charge_status_ambiguous(tmp_path):
    w, contract = _setup(tmp_path)
    with w.conn() as c:
        c.execute("UPDATE charges SET status='pending_unknown'")
    assert verify(w.db_path, contract).outcome == "INDETERMINATE"


def test_indeterminate_when_state_missing(tmp_path):
    _, contract = _setup(tmp_path)
    assert verify(tmp_path / "missing.db", contract).outcome == "INDETERMINATE"


def test_verifier_cannot_write(tmp_path):
    w, contract = _setup(tmp_path)
    ro = World(w.db_path, readonly=True)
    import sqlite3

    import pytest
    with pytest.raises(sqlite3.OperationalError), ro.conn() as c:
        c.execute("UPDATE accounts SET plan='pro'")
