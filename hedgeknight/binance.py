from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any


MARK_PRICE_TOOL = "futures_usds.markPrice"
RULES_TOOL = "futures_usds.exchangeInformation"
SPOT_ACCOUNT_TOOL = "spot.getAccount"
BALANCE_TOOL = "futures_usds.futuresAccountBalanceV3"
POSITIONS_TOOL = "futures_usds.positionInformationV2"
READ_TOOLS = {
    "mark_price": MARK_PRICE_TOOL,
    "symbol_rules": RULES_TOOL,
    "spot_account": SPOT_ACCOUNT_TOOL,
    "futures_balances": BALANCE_TOOL,
    "positions": POSITIONS_TOOL,
}


class BinanceEvidenceError(ValueError):
    pass


def _decimal(value: Any, field: str) -> str:
    try:
        number = Decimal(str(value))
    except Exception as exc:
        raise BinanceEvidenceError(f"{field} must be numeric") from exc
    if not number.is_finite():
        raise BinanceEvidenceError(f"{field} must be finite")
    return format(number, "f")


def _symbol_rules(raw: dict[str, Any], symbol: str) -> dict[str, Any]:
    candidates = raw.get("symbols") if isinstance(raw, dict) else None
    if candidates is None and raw.get("symbol") == symbol:
        candidates = [raw]
    item = next((row for row in candidates or [] if row.get("symbol") == symbol), None)
    if not item:
        raise BinanceEvidenceError(f"{symbol} is absent from exchange information")
    filters = {row.get("filterType"): row for row in item.get("filters", [])}
    lot, price, notional = filters.get("LOT_SIZE", {}), filters.get("PRICE_FILTER", {}), filters.get("MIN_NOTIONAL", {})
    required = {"step_size": lot.get("stepSize"), "min_quantity": lot.get("minQty"), "tick_size": price.get("tickSize"), "min_notional": notional.get("notional")}
    if not all(required.values()):
        raise BinanceEvidenceError("Binance symbol rules are incomplete")
    return {"status": item.get("status"), **{key: _decimal(value, key) for key, value in required.items()}}


def normalize_snapshot(raw: dict[str, Any], *, symbol: str = "BNBUSDT") -> dict[str, Any]:
    tools = raw.get("tools", {})
    for key, expected in READ_TOOLS.items():
        if tools.get(key) != expected:
            raise BinanceEvidenceError(f"{key} must come from {expected}")

    mark = raw.get("mark_price") or {}
    if mark.get("symbol") != symbol:
        raise BinanceEvidenceError("mark price symbol mismatch")
    rules = _symbol_rules(raw.get("symbol_rules") or {}, symbol)
    if rules["status"] != "TRADING":
        raise BinanceEvidenceError(f"{symbol} is not trading")

    spot_account = raw.get("spot_account") or {}
    balances = spot_account.get("balances") or []
    bnb = next((row for row in balances if row.get("asset") == "BNB"), {})
    spot_bnb = Decimal(_decimal(bnb.get("free", "0"), "spot BNB free")) + Decimal(_decimal(bnb.get("locked", "0"), "spot BNB locked"))

    futures_balances = raw.get("futures_balances") or []
    usdt = next((row for row in futures_balances if row.get("asset") == "USDT"), {})
    positions = [row for row in (raw.get("positions") or []) if row.get("symbol") == symbol]
    position_amount = sum((Decimal(_decimal(row.get("positionAmt", "0"), "position amount")) for row in positions), Decimal("0"))
    source_time = mark.get("time")
    if not isinstance(source_time, int) or source_time <= 0:
        raise BinanceEvidenceError("mark price time must be a positive millisecond timestamp")

    return {
        "symbol": symbol,
        "spot_price": _decimal(mark.get("indexPrice"), "index price"),
        "perpetual_price": _decimal(mark.get("markPrice"), "mark price"),
        "funding_rate": _decimal(mark.get("lastFundingRate"), "funding rate"),
        "min_notional": rules["min_notional"],
        "step_size": rules["step_size"],
        "min_quantity": rules["min_quantity"],
        "tick_size": rules["tick_size"],
        "symbol_status": rules["status"],
        "spot_bnb": format(spot_bnb, "f"),
        "futures_usdt_balance": _decimal(usdt.get("balance", "0"), "futures USDT balance"),
        "futures_usdt_available": _decimal(usdt.get("availableBalance", "0"), "futures USDT available"),
        "position_amount": format(position_amount, "f"),
        "source": "Official Binance MCP (live read-only)",
        "source_tools": list(READ_TOOLS.values()),
        "source_tool": MARK_PRICE_TOOL,
        "retrieved_at": datetime.fromtimestamp(source_time / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "verification": "connected",
        "account_verified": True,
    }
