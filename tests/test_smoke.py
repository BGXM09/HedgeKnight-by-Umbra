import json
from datetime import datetime, timezone

import pytest
from hedgeknight.engine import HedgeEngine, HedgeError, SCENARIOS, canonical_digest


def binance_snapshot(*, spot_bnb="10", position_amt="0", available="10000", mark_time=None):
    mark_time = mark_time or int(datetime.now(timezone.utc).timestamp() * 1000)
    return {
        "tools": {
            "mark_price": "futures_usds.markPrice",
            "symbol_rules": "futures_usds.exchangeInformation",
            "spot_account": "spot.getAccount",
            "futures_balances": "futures_usds.futuresAccountBalanceV3",
            "positions": "futures_usds.positionInformationV2",
        },
        "mark_price": {"symbol":"BNBUSDT", "markPrice":"753.65", "indexPrice":"753.38", "lastFundingRate":"0.0001", "time":mark_time},
        "symbol_rules": {"symbols":[{"symbol":"BNBUSDT", "status":"TRADING", "filters":[
            {"filterType":"PRICE_FILTER", "tickSize":"0.010"},
            {"filterType":"LOT_SIZE", "minQty":"0.01", "stepSize":"0.01"},
            {"filterType":"MIN_NOTIONAL", "notional":"5"},
        ]}]},
        "spot_account": {"balances":[{"asset":"BNB", "free":spot_bnb, "locked":"0"}]},
        "futures_balances": [{"asset":"USDT", "balance":available, "availableBalance":available}],
        "positions": [{"symbol":"BNBUSDT", "positionAmt":position_amt}],
    }


@pytest.fixture
def engine(tmp_path):
    value = HedgeEngine(tmp_path / "test.db")
    value.ingest_binance_snapshot(binance_snapshot())
    return value


def test_binance_read_snapshot_normalizes_market_account_and_position(tmp_path):
    engine = HedgeEngine(tmp_path / "integration.db")
    evidence = engine.ingest_binance_snapshot(binance_snapshot(spot_bnb="3.5", position_amt="-1.25", available="42"))
    assert evidence["verification"] == "connected"
    assert evidence["source_tool"] == "futures_usds.markPrice"
    assert evidence["step_size"] == "0.01"
    assert evidence["min_notional"] == "5"
    assert engine.exposure()["spot_bnb"] == "3.500"
    assert engine.exposure()["live_short_bnb"] == "1.250"
    assert engine.exposure()["futures_usdt_available"] == "42"


def test_binance_snapshot_rejects_wrong_tool_and_missing_data(tmp_path):
    engine = HedgeEngine(tmp_path / "failure.db")
    wrong = binance_snapshot()
    wrong["tools"]["positions"] = "futures_usds.newOrder"
    with pytest.raises(HedgeError) as exc: engine.ingest_binance_snapshot(wrong)
    assert exc.value.code == "INVALID_BINANCE_EVIDENCE"
    with pytest.raises(HedgeError) as exc: engine.propose(intent())
    assert exc.value.code == "BINANCE_EVIDENCE_UNAVAILABLE"


def test_non_connected_and_future_evidence_fail_closed(engine):
    plan = engine.propose(intent(), {"verification": "replay"})
    assert next(c for c in plan["risk"]["checks"] if c["code"] == "UNVERIFIED_SOURCE")["status"] == "block"
    plan = engine.propose(intent(), {"retrieved_at": "2999-01-01T00:00:00Z"})
    assert next(c for c in plan["risk"]["checks"] if c["code"] == "STALE_DATA")["status"] == "block"


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
