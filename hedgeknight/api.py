from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from .engine import HedgeEngine, HedgeError, SCENARIOS

engine = HedgeEngine(os.getenv("HEDGEKNIGHT_DB", "data/hedgeknight.db"))
app = FastAPI(title="HedgeKnight API", version="1.0.0", description="Deterministic BNB hedge planning and simulated execution.")
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("UI_ORIGIN", "http://localhost:3000")], allow_methods=["*"], allow_headers=["*"])


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ParseBody(StrictModel):
    command: str = Field(min_length=8, max_length=500)


class IntentBody(StrictModel):
    asset: str = "BNB"
    symbol: str = "BNBUSDT"
    spot_quantity: str = "10"
    target_ratio: str
    duration_hours: int = Field(ge=1, le=168)
    leverage: int = Field(ge=1, le=100)
    execution: str = "simulated"
    source_command: str = "Direct controls"


class ConfirmBody(StrictModel):
    plan_id: str


class KillBody(StrictModel):
    enabled: bool


@app.exception_handler(HedgeError)
async def hedge_error(_: Request, exc: HedgeError):
    return JSONResponse({"error": {"code": exc.code, "message": exc.message}}, status_code=exc.status)


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError):
    return JSONResponse({"error": {"code": "INVALID_REQUEST", "message": "Request schema validation failed.", "details": exc.errors()}}, status_code=422)


@app.get("/health")
def health(): return {"status": "ok", "mode": "demo", "execution": "simulated"}


@app.get("/api/status")
def status(): return engine.status()


@app.get("/api/exposure")
def exposure(): return engine.exposure()


@app.get("/api/market")
def market(): return engine.market()


@app.post("/api/intents/parse")
def parse(body: ParseBody): return engine.parse_intent(body.command)


@app.post("/api/plans")
def plans(body: IntentBody): return engine.propose(body.model_dump())


@app.post("/api/plans/{plan_id}/confirm")
def confirm(plan_id: str, body: ConfirmBody):
    if body.plan_id != plan_id: raise HedgeError("PLAN_ID_MISMATCH", "Confirm the exact plan ID shown in the proposal.")
    return engine.confirm(plan_id)


@app.post("/api/plans/{plan_id}/simulate")
def simulate(plan_id: str): return engine.simulate(plan_id)


@app.get("/api/positions/active")
def position(): return engine.active_position()


@app.post("/api/positions/{position_id}/unwind-plan")
def unwind_plan(position_id: str): return engine.propose_unwind(position_id)


@app.post("/api/positions/{position_id}/unwind-simulate")
def unwind(position_id: str): return engine.simulate_unwind(position_id)


@app.get("/api/receipts")
def receipts(): return engine.receipts()


@app.get("/api/receipts/{receipt_id}")
def receipt(receipt_id: str): return engine.receipt(receipt_id)


@app.get("/api/scenarios")
def scenarios(): return SCENARIOS


@app.post("/api/scenarios/{scenario_id}/load")
def scenario(scenario_id: str): return engine.load_scenario(scenario_id)


@app.post("/api/settings/kill-switch")
def kill(body: KillBody): return engine.set_kill_switch(body.enabled)


@app.get("/api/events")
async def events():
    async def stream():
        stages = ["evidence_loaded", "intent_interpreted", "proposal_calculated", "risk_evaluated"]
        for stage in stages:
            yield f"event: workflow\ndata: {json.dumps({'stage': stage, 'mode': 'demo', 'execution': 'simulated'})}\n\n"
            await asyncio.sleep(.12)
    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/mcp-info")
def mcp_info():
    return {"endpoint": "/mcp", "transport": "streamable-http", "tools": 10, "note": "Mount is active when the optional MCP SDK is installed."}


try:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("HedgeKnight", stateless_http=True, json_response=True, streamable_http_path="/")

    @mcp.tool(description="Report HedgeKnight mode, data source, safety state, and execution availability.")
    def hedgeknight_status() -> dict[str, Any]: return engine.status()

    @mcp.tool(description="Inspect Spot BNB, simulated short, net exposure, and effective hedge ratio.")
    def hedgeknight_exposure() -> dict[str, Any]: return engine.exposure()

    @mcp.tool(description="Estimate opening, funding, closing, and total costs for a BNB hedge.")
    def hedgeknight_funding_cost(target_ratio: float, duration_hours: int, leverage: int = 2) -> dict[str, Any]:
        intent = {"asset":"BNB","symbol":"BNBUSDT","spot_quantity":"10","target_ratio":str(target_ratio),"duration_hours":duration_hours,"leverage":leverage,"execution":"simulated","source_command":"MCP cost estimate"}
        return engine.propose(intent)["proposal"]

    @mcp.tool(description="Create an expiring simulated BNB hedge plan from normalized evidence and intent.")
    def hedgeknight_propose_hedge(target_ratio: float, duration_hours: int, leverage: int = 2) -> dict[str, Any]:
        return engine.propose({"asset":"BNB","symbol":"BNBUSDT","spot_quantity":"10","target_ratio":str(target_ratio),"duration_hours":duration_hours,"leverage":leverage,"execution":"simulated","source_command":"MCP proposal"})

    @mcp.tool(description="Return the stable ordered deterministic risk decision for a stored plan.")
    def hedgeknight_evaluate_risk(plan_id: str) -> dict[str, Any]: return engine._plan(plan_id)["risk"]

    @mcp.tool(description="Explicitly confirm one exact, unexpired simulated hedge plan.")
    def hedgeknight_confirm_plan(plan_id: str) -> dict[str, Any]: return engine.confirm(plan_id)

    @mcp.tool(description="Run the single-use simulated order lifecycle for a confirmed plan.")
    def hedgeknight_simulate_execution(plan_id: str) -> dict[str, Any]: return engine.simulate(plan_id)

    @mcp.tool(description="Monitor the active simulated BNB hedge and current net exposure.")
    def hedgeknight_monitor_hedge() -> dict[str, Any]: return {"position": engine.active_position(), "exposure": engine.exposure()}

    @mcp.tool(description="Prepare a bounded reduce-only unwind for the remaining simulated short position.")
    def hedgeknight_propose_unwind(position_id: str) -> dict[str, Any]: return engine.propose_unwind(position_id)

    @mcp.tool(description="Retrieve one tamper-evident simulated lifecycle receipt by its identifier.")
    def hedgeknight_receipt(receipt_id: str) -> dict[str, Any]: return engine.receipt(receipt_id)

    mcp_app = mcp.streamable_http_app()
    app.mount("/mcp", mcp_app)
    app.router.lifespan_context = mcp_app.router.lifespan_context
except ImportError:
    mcp = None

    @mcp.tool(description="Prepare a bounded reduce-only proposal for the remaining simulated short.")
    def hedgeknight_propose_unwind(position_id: str) -> dict[str, Any]: return engine.propose_unwind(position_id)

    @mcp.tool(description="Retrieve a tamper-evident simulated execution receipt by identifier.")
    def hedgeknight_receipt(receipt_id: str) -> dict[str, Any]: return engine.receipt(receipt_id)

    app.mount("/mcp", mcp.streamable_http_app())
except ImportError:
    pass
