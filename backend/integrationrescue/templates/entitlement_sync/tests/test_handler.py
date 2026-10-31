from sync.handler import handle, resolve_plan

CFG = {"price_plan_map": {"price_a": "pro", "price_b": "free"}}


def _event(price_id: str, etype: str = "invoice.paid") -> dict:
    return {"id": "evt_t", "type": etype,
            "data": {"customer_id": "cus_t", "lines": [{"price_id": price_id}]}}


def test_maps_known_price_to_plan():
    out = handle(_event("price_a"), CFG)
    assert out["status"] == "ok"
    assert out["actions"] == [{"op": "set_plan", "customer_id": "cus_t", "plan": "pro"}]


def test_ignores_other_event_types():
    assert handle(_event("price_a", "invoice.created"), CFG)["actions"] == []


def test_unknown_price_makes_no_change():
    assert resolve_plan("price_zzz", CFG) is None
    assert handle(_event("price_zzz"), CFG)["actions"] == []
