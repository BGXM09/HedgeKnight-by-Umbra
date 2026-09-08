import json

import pytest

from hedgeknight.engine import HedgeEngine, HedgeError, SCENARIOS, canonical_digest


@pytest.fixture
def engine(tmp_path): return HedgeEngine(tmp_path / "test.db")


def intent(ratio="50", duration=24, leverage=2):
    return {"asset":"BNB","symbol":"BNBUSDT","spot_quantity":"10","target_ratio":ratio,"duration_hours":duration,"leverage":leverage,"execution":"simulated","source_command":"I hold 10 BNB. Hedge 50% for 24 hours."}


def test_hedge_sizing_and_happy_path(engine):
    plan = engine.propose(intent())
    assert plan["proposal"]["required_adjustment"] == "5.000"
    assert plan["proposal"]["net_exposure_after"] == "5.000"
    assert plan["risk"]["decision"] == "approved"
    engine.confirm(plan["plan_id"])
    result = engine.simulate(plan["plan_id"])
    assert result["state"] == "completed"
    assert result["position"]["execution"] == "simulated"


@pytest.mark.parametrize("scenario_id,code", [
    ("leverage-10x","LEVERAGE_LIMIT"),("over-hedge","INVALID_HEDGE_RATIO"),
    ("stale-evidence","STALE_DATA"),("unverified-source","UNVERIFIED_SOURCE"),
    ("funding-limit","FUNDING_COST_LIMIT"),("expired-plan","PLAN_EXPIRED"),
    ("duplicate-plan","DUPLICATE_PLAN"),("kill-switch","KILL_SWITCH")])
def test_blocked_scenarios(engine, scenario_id, code):
    result = engine.load_scenario(scenario_id)
    failed = [c["code"] for c in result["plan"]["risk"]["checks"] if c["status"] == "block"]
    assert code in failed


def test_duplicate_and_receipt_hash(engine):
    plan=engine.propose(intent()); engine.confirm(plan["plan_id"]); result=engine.simulate(plan["plan_id"])
    receipt=result["receipt"]
    assert canonical_digest(receipt)==receipt["digest"]
    with pytest.raises(HedgeError, match="already executed"): engine.simulate(plan["plan_id"])


def test_reduce_only_unwind(engine):
    plan=engine.propose(intent()); engine.confirm(plan["plan_id"]); opened=engine.simulate(plan["plan_id"])
    position=opened["position"]
    proposal=engine.propose_unwind(position["position_id"])
    assert proposal["reduce_only"] and proposal["quantity"]=="5.000"
    closed=engine.simulate_unwind(position["position_id"])
    assert closed["position"]["remaining_quantity"]=="0.000"
    assert closed["receipt"]["parent_receipt_id"]==opened["receipt"]["receipt_id"]
