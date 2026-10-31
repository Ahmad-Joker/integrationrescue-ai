from integrationrescue.simulators.world import World


def _world(tmp_path):
    w = World(tmp_path / "w.db")
    w.add_price("price_pro", "pro", 2900)
    ids = w.create_customer("acme", "a@acme.example", "A")
    return w, ids


def _granting_subscriber(world, event):
    done = world.query("SELECT 1 FROM processed_events WHERE event_id=?", (event["id"],))
    if done:
        return 200, "duplicate ignored"
    world.set_plan(event["data"]["customer_id"], "pro", event["id"])
    with world.conn() as c:
        c.execute("INSERT INTO processed_events VALUES(?, 'applied', 'now')", (event["id"],))
    return 202, "ok"


def test_payment_is_idempotent(tmp_path):
    w, ids = _world(tmp_path)
    first = w.pay(ids["customer_id"], "price_pro", "key-1")
    second = w.pay(ids["customer_id"], "price_pro", "key-1")
    assert second["idempotent_replay"] is True
    assert second["charge_id"] == first["charge_id"]
    assert len(w.query("SELECT * FROM charges")) == 1


def test_duplicate_delivery_fault_delivers_twice(tmp_path):
    w, ids = _world(tmp_path)
    pay = w.pay(ids["customer_id"], "price_pro", "k")
    w.set_fault("duplicate_delivery")
    w.deliver(pay["event_id"], _granting_subscriber)
    assert len(w.query("SELECT * FROM deliveries")) == 2
    assert len(w.query("SELECT * FROM entitlement_audit")) == 1  # receiver dedups


def test_lost_ack_causes_retry_after_commit(tmp_path):
    w, ids = _world(tmp_path)
    pay = w.pay(ids["customer_id"], "price_pro", "k")
    w.set_fault("lost_ack")
    res = w.deliver(pay["event_id"], _granting_subscriber)
    rows = w.query("SELECT status FROM deliveries ORDER BY attempt")
    assert [r["status"] for r in rows] == ["timeout", "delivered"]
    assert res.final_status == "delivered"
    assert w.account_for_customer(ids["customer_id"])["plan"] == "pro"
    assert len(w.query("SELECT * FROM entitlement_audit")) == 1


def test_subscriber_crash_is_retried_and_recorded(tmp_path):
    w, ids = _world(tmp_path)
    pay = w.pay(ids["customer_id"], "price_pro", "k")

    def boom(world, event):
        raise RuntimeError("kaput")

    res = w.deliver(pay["event_id"], boom, max_attempts=3)
    assert res.final_status == "failed"
    assert {r["http_status"] for r in w.query("SELECT * FROM deliveries")} == {500}


def test_clone_is_isolated(tmp_path):
    w, ids = _world(tmp_path)
    clone = w.clone_to(tmp_path / "clone.db")
    clone.set_plan(ids["customer_id"], "pro", "evt_x")
    assert w.account_for_customer(ids["customer_id"])["plan"] == "free"
