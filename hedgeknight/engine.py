from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_DOWN
from pathlib import Path
from typing import Any

D = Decimal
QTY_STEP = D("0.001")
DEMO_MAX_NOTIONAL = D("100000")
FUNDING_LIMIT = D("75")
PLAN_TTL_SECONDS = 300


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime | None = None) -> str:
    return (value or now()).isoformat().replace("+00:00", "Z")


def dec(value: Any) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("boolean is not numeric")
    result = D(str(value))
    if not result.is_finite():
        raise ValueError("number must be finite")
    return result


def money(value: Decimal) -> str:
    return f"{value.quantize(D('0.01')):f}"


def quantity(value: Decimal) -> str:
    return f"{value.quantize(QTY_STEP, rounding=ROUND_DOWN):f}"


def canonical_digest(payload: dict[str, Any]) -> str:
    clean = {k: v for k, v in payload.items() if k != "digest"}
    blob = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()


@dataclass(frozen=True)
class MarketEvidence:
    spot_price: str = "612.40"
    perpetual_price: str = "611.90"
    funding_rate: str = "0.0001"
    min_notional: str = "5"
    source: str = "Binance public market replay"
    source_tool: str | None = None
    retrieved_at: str = "2026-09-08T12:00:00Z"
    verification: str = "replay"
    fixture_id: str = "bnbusdt-replay-2026-09-08"


SCENARIOS: list[dict[str, Any]] = [
    {"id": "valid-50", "label": "Valid 50% · 24 hours", "ratio": 50, "duration": 24, "leverage": 2, "outcome": "approved"},
    {"id": "leverage-10x", "label": "10× leverage", "ratio": 50, "duration": 24, "leverage": 10, "outcome": "blocked"},
    {"id": "over-hedge", "label": "125% hedge", "ratio": 125, "duration": 24, "leverage": 2, "outcome": "blocked"},
    {"id": "stale-evidence", "label": "Stale market evidence", "ratio": 50, "duration": 24, "leverage": 2, "outcome": "blocked", "stale": True},
    {"id": "unverified-source", "label": "Unverified connected source", "ratio": 50, "duration": 24, "leverage": 2, "outcome": "blocked", "connected": True, "unverified": True},
    {"id": "funding-limit", "label": "Funding cost above limit", "ratio": 100, "duration": 168, "leverage": 1, "outcome": "blocked", "funding_rate": "0.025"},
    {"id": "expired-plan", "label": "Expired plan", "ratio": 50, "duration": 24, "leverage": 2, "outcome": "blocked", "expired": True},
    {"id": "duplicate-plan", "label": "Duplicate execution", "ratio": 50, "duration": 24, "leverage": 2, "outcome": "blocked", "duplicate": True},
    {"id": "kill-switch", "label": "Kill switch enabled", "ratio": 50, "duration": 24, "leverage": 2, "outcome": "blocked", "kill_switch": True},
    {"id": "valid-unwind", "label": "Valid reduce-only unwind", "ratio": 50, "duration": 24, "leverage": 2, "outcome": "approved", "unwind": True},
]


class HedgeError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code, self.message, self.status = code, message, status
        super().__init__(message)


class HedgeEngine:
    def __init__(self, db_path: str | Path = "data/hedgeknight.db"):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.db_path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self._setup()

    def _setup(self) -> None:
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS plans (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS positions (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS receipts (id TEXT PRIMARY KEY, payload TEXT NOT NULL, created_at TEXT NOT NULL);
        """)
        self.db.execute("INSERT OR IGNORE INTO state VALUES ('kill_switch','false')")
        self.db.commit()

    def _state(self, key: str, default: Any = None) -> Any:
        row = self.db.execute("SELECT value FROM state WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set_kill_switch(self, enabled: bool) -> dict[str, Any]:
        self.db.execute("INSERT OR REPLACE INTO state VALUES ('kill_switch',?)", (json.dumps(enabled),))
        self.db.commit()
        return self.status()

    def status(self) -> dict[str, Any]:
        return {"product": "HedgeKnight — by Umbra", "mode": "demo", "execution": "simulated", "market_source": "replay", "kill_switch": self._state("kill_switch", False), "live_execution": "unavailable", "time": iso()}

    def market(self, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
        data = asdict(MarketEvidence())
        data.update(overrides or {})
        return data

    def active_position(self) -> dict[str, Any] | None:
        row = self.db.execute("SELECT payload FROM positions ORDER BY rowid DESC LIMIT 1").fetchone()
        return json.loads(row[0]) if row else None

    def exposure(self) -> dict[str, Any]:
        pos = self.active_position()
        short = dec(pos["remaining_quantity"]) if pos and pos["state"] == "open" else D("0")
        spot = D("10")
        return {"spot_bnb": quantity(spot), "simulated_short_bnb": quantity(short), "net_bnb": quantity(spot-short), "effective_hedge_percent": money(short/spot*100), "mode": "demo", "execution": "simulated"}

    def parse_intent(self, command: str) -> dict[str, Any]:
        ratio = re.search(r"(\d+(?:\.\d+)?)\s*%", command)
        duration = re.search(r"(\d+)\s*(hour|hours|day|days|week|weeks)", command, re.I)
        holding = re.search(r"(?:hold|have|own)\s+(\d+(?:\.\d+)?)\s*BNB", command, re.I)
        if not ratio or not duration:
            raise HedgeError("MALFORMED_INTENT", "Include a hedge percentage and duration, for example 50% for 24 hours.")
        n, unit = int(duration.group(1)), duration.group(2).lower()
        hours = n * (168 if "week" in unit else 24 if "day" in unit else 1)
        return {"asset": "BNB", "symbol": "BNBUSDT", "spot_quantity": holding.group(1) if holding else "10", "target_ratio": ratio.group(1), "duration_hours": hours, "leverage": 2, "source_command": command}

    def _checks(self, intent: dict[str, Any], market: dict[str, Any], proposal: dict[str, Any], *, expired=False, duplicate=False) -> list[dict[str, Any]]:
        ratio, lev = dec(intent["target_ratio"]), dec(intent["leverage"])
        retrieved = datetime.fromisoformat(market["retrieved_at"].replace("Z", "+00:00"))
        connected = market.get("verification") == "connected"
        candidates = [
            ("KILL_SWITCH", not self._state("kill_switch", False), "Disable the kill switch to create a new plan."),
            ("REAL_EXECUTION_DISABLED", intent.get("execution", "simulated") == "simulated", "Select simulated execution; live execution is unavailable."),
            ("MALFORMED_EVIDENCE", all(market.get(k) for k in ("perpetual_price", "funding_rate", "min_notional", "source", "retrieved_at")), "Provide complete market evidence with units and retrieval time."),
            ("UNVERIFIED_SOURCE", not connected or bool(market.get("source_tool")), "Connected data needs an observed official Binance MCP source tool."),
            ("STALE_DATA", now() - retrieved <= timedelta(days=365) and not market.get("force_stale"), "Refresh the market evidence before proposing the hedge."),
            ("SYMBOL_NOT_ALLOWED", intent.get("symbol") == "BNBUSDT", "Only BNBUSDT is supported in this demo."),
            ("INVALID_HEDGE_RATIO", D("1") <= ratio <= D("100"), "Choose a hedge ratio from 1% to 100%."),
            ("OVER_HEDGE", ratio <= D("100"), "Reduce the target so the simulated short does not exceed Spot BNB."),
            ("LEVERAGE_LIMIT", lev <= D("2"), "Use 2× leverage or less."),
            ("NOTIONAL_LIMIT", dec(market["min_notional"]) <= dec(proposal["hedge_notional"]) <= DEMO_MAX_NOTIONAL, "Choose a notional within symbol minimum and the demo ceiling."),
            ("FUNDING_COST_LIMIT", dec(proposal["projected_funding"]) <= FUNDING_LIMIT, "Shorten the duration or reduce the hedge ratio."),
            ("PLAN_EXPIRED", not expired, "Create a fresh plan and confirm it within five minutes."),
            ("DUPLICATE_PLAN", not duplicate, "This single-use plan was already executed; create a new plan."),
        ]
        return [{"code": code, "status": "pass" if ok else "block", "explanation": "Check passed." if ok else fix} for code, ok, fix in candidates]

    def propose(self, intent: dict[str, Any], market_overrides: dict[str, Any] | None = None, scenario: dict[str, Any] | None = None) -> dict[str, Any]:
        scenario = scenario or {}
        market = self.market(market_overrides)
        spot, ratio, lev = dec(intent.get("spot_quantity", 10)), dec(intent["target_ratio"]), dec(intent.get("leverage", 2))
        current = dec(self.exposure()["simulated_short_bnb"])
        target = spot * ratio / 100
        adjustment = max(D("0"), target-current).quantize(QTY_STEP, rounding=ROUND_DOWN)
        price, duration = dec(market["perpetual_price"]), dec(intent["duration_hours"])
        notional = adjustment * price
        opening_fee = notional * D("0.0004")
        closing_fee = notional * D("0.0004")
        funding = abs(notional * dec(market["funding_rate"]) * duration / D("8"))
        proposal = {"spot_quantity": quantity(spot), "existing_short": quantity(current), "required_adjustment": quantity(adjustment), "target_short": quantity(target), "net_exposure_before": quantity(spot-current), "net_exposure_after": quantity(spot-target), "hedge_percent_after": money(ratio), "reference_price": money(price), "hedge_notional": money(notional), "estimated_margin": money(notional/lev if lev else D("0")), "opening_fee": money(opening_fee), "projected_funding": money(funding), "closing_fee": money(closing_fee), "total_estimated_cost": money(opening_fee+funding+closing_fee), "slippage_bps": "2", "duration_hours": int(duration)}
        checks = self._checks(intent, market, proposal, expired=scenario.get("expired", False), duplicate=scenario.get("duplicate", False))
        plan = {"plan_id": str(uuid.uuid4()), "created_at": iso(), "expires_at": iso(now()+timedelta(seconds=PLAN_TTL_SECONDS)), "nonce": str(uuid.uuid4()), "state": "blocked" if any(c["status"] == "block" for c in checks) else "proposed", "mode": "demo", "execution": "simulated", "intent": intent, "market_evidence": market, "proposal": proposal, "risk": {"decision": "blocked" if any(c["status"] == "block" for c in checks) else "approved", "checks": checks}}
        self.db.execute("INSERT INTO plans VALUES (?,?)", (plan["plan_id"], json.dumps(plan)))
        self.db.commit()
        return plan

    def _plan(self, plan_id: str) -> dict[str, Any]:
        row = self.db.execute("SELECT payload FROM plans WHERE id=?", (plan_id,)).fetchone()
        if not row: raise HedgeError("PLAN_NOT_FOUND", "The requested plan does not exist.", 404)
        return json.loads(row[0])

    def _save_plan(self, plan: dict[str, Any]) -> None:
        self.db.execute("UPDATE plans SET payload=? WHERE id=?", (json.dumps(plan), plan["plan_id"]))
        self.db.commit()

    def confirm(self, plan_id: str) -> dict[str, Any]:
        plan = self._plan(plan_id)
        if plan["state"] == "blocked": raise HedgeError("RISK_BLOCKED", "This plan failed deterministic risk checks.")
        if now() > datetime.fromisoformat(plan["expires_at"].replace("Z", "+00:00")): raise HedgeError("PLAN_EXPIRED", "Create a fresh plan and confirm it within five minutes.")
        if plan["state"] != "proposed": raise HedgeError("DUPLICATE_PLAN", "This plan is not awaiting confirmation.")
        plan.update(state="confirmed", confirmed_at=iso())
        self._save_plan(plan)
        return plan

    def simulate(self, plan_id: str) -> dict[str, Any]:
        plan = self._plan(plan_id)
        if plan["state"] == "completed": raise HedgeError("DUPLICATE_PLAN", "This single-use plan was already executed.")
        if plan["state"] != "confirmed": raise HedgeError("CONFIRMATION_REQUIRED", "Confirm the exact current plan before simulation.")
        p, price = plan["proposal"], dec(plan["proposal"]["reference_price"])
        fill = price * D("0.9998")
        position = {"position_id": str(uuid.uuid4()), "plan_id": plan_id, "symbol": "BNBUSDT", "side": "short", "opening_quantity": p["required_adjustment"], "remaining_quantity": p["required_adjustment"], "entry_price": money(fill), "mark_price": money(price), "simulated_pnl": "0.00", "hedge_ratio": p["hedge_percent_after"], "expires_at": iso(now()+timedelta(hours=int(p["duration_hours"]))), "state": "open", "mode": "demo", "execution": "simulated", "reduce_only": False}
        self.db.execute("INSERT INTO positions VALUES (?,?)", (position["position_id"], json.dumps(position)))
        plan["state"] = "completed"; self._save_plan(plan)
        receipt = self._receipt(plan, position, "opening")
        return {"state": "completed", "stages": ["preparing", "simulating_fill", "recording_position", "completed"], "position": position, "receipt": receipt}

    def _receipt(self, plan: dict[str, Any], position: dict[str, Any], kind: str, parent: str | None = None) -> dict[str, Any]:
        receipt = {"receipt_id": str(uuid.uuid4()), "kind": kind, "plan_id": plan["plan_id"], "parent_receipt_id": parent, "created_at": iso(), "mode": "demo", "execution": "simulated", "requested_command": plan["intent"].get("source_command"), "normalized_intent": plan["intent"], "evidence": plan["market_evidence"], "proposal": plan["proposal"], "risk": plan["risk"], "confirmation_timestamp": plan.get("confirmed_at"), "position": position, "final_state": "completed"}
        receipt["digest"] = canonical_digest(receipt)
        self.db.execute("INSERT INTO receipts VALUES (?,?,?)", (receipt["receipt_id"], json.dumps(receipt), receipt["created_at"]))
        self.db.commit(); return receipt

    def receipts(self) -> list[dict[str, Any]]:
        return [json.loads(r[0]) for r in self.db.execute("SELECT payload FROM receipts ORDER BY created_at DESC")]

    def receipt(self, receipt_id: str) -> dict[str, Any]:
        row = self.db.execute("SELECT payload FROM receipts WHERE id=?", (receipt_id,)).fetchone()
        if not row: raise HedgeError("RECEIPT_NOT_FOUND", "Receipt not found.", 404)
        return json.loads(row[0])

    def propose_unwind(self, position_id: str) -> dict[str, Any]:
        row = self.db.execute("SELECT payload FROM positions WHERE id=?", (position_id,)).fetchone()
        if not row: raise HedgeError("POSITION_NOT_FOUND", "Position not found.", 404)
        pos = json.loads(row[0])
        if pos["state"] != "open" or dec(pos["remaining_quantity"]) <= 0: raise HedgeError("UNWIND_BOUND", "Only the remaining open simulated short may be closed.")
        intent = {"asset": "BNB", "symbol": "BNBUSDT", "spot_quantity": "10", "target_ratio": "0", "duration_hours": 0, "leverage": 1, "execution": "simulated", "source_command": "Reduce-only unwind"}
        return {"unwind_plan_id": str(uuid.uuid4()), "position_id": position_id, "side": "buy", "quantity": pos["remaining_quantity"], "reduce_only": True, "state": "proposed", "mode": "demo", "execution": "simulated", "intent": intent}

    def simulate_unwind(self, position_id: str) -> dict[str, Any]:
        row = self.db.execute("SELECT payload FROM positions WHERE id=?", (position_id,)).fetchone()
        if not row: raise HedgeError("POSITION_NOT_FOUND", "Position not found.", 404)
        pos = json.loads(row[0])
        if pos["state"] != "open": raise HedgeError("UNWIND_BOUND", "This position has no remaining simulated short.")
        parent = next((r for r in self.receipts() if r["position"]["position_id"] == position_id and r["kind"] == "opening"), None)
        pos.update(state="closed", remaining_quantity="0.000", reduce_only=True)
        self.db.execute("UPDATE positions SET payload=? WHERE id=?", (json.dumps(pos), position_id)); self.db.commit()
        plan = self._plan(pos["plan_id"])
        receipt = self._receipt(plan, pos, "closing", parent["receipt_id"] if parent else None)
        return {"state": "completed", "position": pos, "receipt": receipt}

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        scenario = next((s for s in SCENARIOS if s["id"] == scenario_id), None)
        if not scenario: raise HedgeError("SCENARIO_NOT_FOUND", "Unknown judge scenario.", 404)
        self.set_kill_switch(bool(scenario.get("kill_switch")))
        market: dict[str, Any] = {}
        if scenario.get("stale"): market["force_stale"] = True
        if scenario.get("connected"): market.update(verification="connected", source="Official Binance MCP evidence", source_tool=None)
        if scenario.get("funding_rate"): market["funding_rate"] = scenario["funding_rate"]
        intent = {"asset": "BNB", "symbol": "BNBUSDT", "spot_quantity": "10", "target_ratio": str(scenario["ratio"]), "duration_hours": scenario["duration"], "leverage": scenario["leverage"], "execution": "simulated", "source_command": scenario["label"]}
        plan = self.propose(intent, market, scenario)
        return {"scenario": scenario, "plan": plan}
