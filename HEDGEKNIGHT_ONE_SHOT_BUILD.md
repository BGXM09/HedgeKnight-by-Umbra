# HEDGEKNIGHT BY UMBRA — ONE-SHOT BUILD SPECIFICATION

## 0. Master instruction to Codex

Read this file completely before modifying the repository. Then build the complete, working hackathon submission described here.

Do not stop after planning, scaffolding, producing a static mockup, or listing next steps. Inspect the existing repository first, preserve useful code, make reasonable implementation decisions autonomously, build the full application, run it, inspect the rendered interface, fix functional and visible defects, run only the minimal smoke checks, and leave the repository deployment-ready.

This is a Demo-first prototype requiring no funded Binance account. Do not place or enable real-money orders. Do not describe simulated activity as live, mainnet, executed, or verified. Never invent Binance MCP tool names or claim that Binance MCP was connected when it was not. If official tool names differ, discover them through MCP tool discovery after authorization.

Optimize for a compelling end-to-end demonstration, excellent interaction design, honest evidence, and clear Binance Agent OS relevance. This is a build sprint, not a testing exercise. Complete and polish the product before writing any nonessential test. Do not waste the sprint on enterprise infrastructure, coverage targets, excessive tests, speculative features, or decorative pages.

### Strict implementation priority

Work in this order and do not allow later items to consume time needed by earlier ones:

1. Working canonical hedge flow from command to receipt.
2. Professional, polished dashboard with complete interactive states.
3. Shared engine, REST/SSE API, and persistent Demo state.
4. Functional HedgeKnight MCP tools and Binance MCP coordination boundary.
5. Judge scenarios, evidence manifest, submission copy, and deployment.
6. Only the minimal smoke checks needed to prove the above still works.

As a rough effort guide, spend approximately 70% on building and polishing the product, 15% on MCP/Agent OS integration, 10% on submission and deployment, and no more than 5% on automated checks. Do not delay a working demo to improve test coverage.

## 1. Product identity

**Product:** HedgeKnight  
**Parent brand:** Umbra  
**Display lockup:** HedgeKnight — by Umbra  
**Category:** Binance Agent OS portfolio-protection agent  
**Primary tagline:** AI-powered portfolio hedging through Binance Agent OS.  

**One-line pitch:**

> HedgeKnight turns a natural-language protection request into a calculated, risk-checked and monitored BNB hedge without requiring the user to sell the underlying asset.

**Canonical demo command:**

> “I hold 10 BNB. Hedge 50% of my exposure for 24 hours.”

HedgeKnight is not a price-prediction bot. It must never promise profit, risk-free protection, guaranteed returns, or protection from every possible loss.

## 2. User problem

A user may want to retain Spot BNB while temporarily reducing sensitivity to a market decline. Manually creating a futures hedge requires exposure calculation, contract sizing, price and funding inspection, margin estimation, safety constraints, order planning, monitoring, and a controlled unwind.

HedgeKnight converts that workflow into one bounded agent operation:

1. Understand the protection instruction.
2. Inspect source-labelled Binance information.
3. Calculate the required short-perpetual hedge.
4. Explain expected exposure, costs, and risks.
5. Run deterministic safety checks.
6. Ask the user to confirm the exact plan.
7. Simulate the fill and resulting position.
8. Monitor the simulated hedge.
9. Propose and simulate a reduce-only unwind.
10. Generate a tamper-evident receipt.

## 3. Hackathon thesis

The official Binance MCP must be functionally relevant, not a logo or decorative integration.

In the submitted no-funds build, Binance MCP supplies source-labelled information such as:

- BNB spot or reference price.
- BNB perpetual price.
- Current or recent funding rate.
- BNBUSDT symbol and contract rules.
- Quantity precision and minimum notional where exposed.
- Optional read-only balance or position evidence when authorization permits.

HedgeKnight supplies the domain intelligence:

- Exposure normalization.
- Hedge sizing.
- Funding-cost estimation.
- Margin estimation.
- Deterministic risk policy.
- Expiring, single-use plans.
- Confirmation state.
- Simulated execution.
- Monitoring and unwind planning.
- Evidence receipts.

The key proof is that an AI client can coordinate the official Binance MCP and HedgeKnight MCP to satisfy a complete user objective. The public website independently makes the same workflow easy for judges to experience.

## 4. Exact architecture

There are two entry points over one shared HedgeKnight engine.

```text
ENTRY POINT A — PUBLIC PRODUCT DEMO

Judge browser
    -> Next.js dashboard
    -> FastAPI REST/SSE API
    -> shared HedgeKnight engine
    -> SQLite demo state and receipts


ENTRY POINT B — BINANCE AGENT OS PROOF

Supported AI client / MCP host
    -> official Binance MCP
         -> market, funding, symbol rules, optional read-only account evidence
    -> HedgeKnight MCP
         -> shared HedgeKnight engine
         -> SQLite demo state and receipts


DEPLOYMENT

VPS
    -> Caddy HTTPS reverse proxy
    -> Next.js dashboard
    -> FastAPI application
         -> REST API
         -> SSE event stream
         -> HedgeKnight MCP streamable HTTP endpoint
         -> shared HedgeKnight engine
         -> SQLite persistent volume
```

### Non-negotiable boundaries

- The website and MCP server use the same engine modules; never duplicate hedge math or risk policy.
- The supported AI client is the orchestrator between official Binance MCP and HedgeKnight MCP.
- The browser never receives Binance passwords, OAuth tokens, private keys, trading keys, or cookies.
- The VPS does not store Binance trading credentials.
- The public demo must work with zero credentials and zero funds.
- Real Binance-sourced inputs and simulated financial actions must remain distinguishable in data, UI, receipts, and documentation.
- Do not fake direct website-to-Binance OAuth.
- Do not silently replace Binance MCP with ordinary REST while labelling it MCP.
- A REST/replay market-data adapter may support the standalone demo only when clearly labelled by its actual source.

## 5. Scope

### Required MVP

- One asset: BNB.
- One pair: BNBUSDT.
- Spot BNB as the underlying exposure.
- Binance USDⓈ-M BNB perpetual as the conceptual hedge instrument.
- 25%, 50%, and 100% hedge presets.
- Custom hedge ratio input from 1% to 100%.
- Maximum displayed leverage: 2x.
- Duration presets: 4 hours, 12 hours, 24 hours, and 7 days.
- Public Demo mode requiring no authentication.
- Optional connected-data mode through official Binance MCP.
- Natural-language demo command input.
- Proposal and confirmation separated by an expiring plan.
- Deterministic risk checks.
- Simulated order lifecycle.
- Hedge monitoring.
- Reduce-only unwind.
- Kill switch.
- JSON evidence receipts.
- Custom HedgeKnight MCP server.
- Agent coordination instructions for using Binance MCP with HedgeKnight MCP.
- Responsive public dashboard.

### Explicitly out of scope

- Real-money execution.
- Deposits or withdrawals.
- Wallet connection.
- Smart contracts.
- Options.
- Multi-asset hedging.
- Cross-exchange arbitrage.
- Yield optimization.
- Automated trading signals.
- Copy or social trading.
- Embedded website chatbot requiring a paid LLM API.
- User accounts and complex authentication.
- Microservices, Kubernetes, queues, vector databases, or enterprise observability.

## 6. Operating modes and truth labels

### Demo mode — default

- Uses a sample portfolio of 10 BNB.
- Requires no secrets, account, funds, or login.
- Uses fresh public Binance-sourced information only when its source is provable.
- Otherwise uses a bundled timestamped replay fixture.
- Simulates transfer, order, fill, position, PnL, monitoring, and unwind.
- Every simulated record contains `mode: "demo"` and `execution: "simulated"`.
- Every page displays a persistent `DEMO — SIMULATED EXECUTION` indicator.

### Connected-data mode — optional

- Receives normalized evidence gathered through official Binance MCP by the AI host.
- May use public data and optional read-only account data.
- Never requires a funded account.
- Still simulates every financial action.
- Displays both `BINANCE MCP DATA` and `SIMULATED EXECUTION` when applicable.

### Live execution

- Explicitly unavailable in this submission.
- Do not expose a functioning Live toggle.
- A disabled control may say `LIVE — NOT AVAILABLE IN THIS DEMO`.
- Reject any API or MCP request attempting a non-simulated execution.

## 7. Shared domain model

Use decimal-safe arithmetic for prices, quantities, money, rates, percentages, and costs.

Core entities:

- `Evidence`: value, unit, source, source tool if known, retrieval time, verification state, fixture ID where applicable.
- `ExposureSnapshot`: Spot BNB, existing simulated futures BNB, net BNB, reference price, USD notional.
- `HedgeIntent`: asset, target ratio, duration, leverage, source command.
- `HedgeProposal`: before/after exposure, adjustment quantity, notional, margin, fees, funding estimate, assumptions.
- `RiskDecision`: ordered checks, pass/block result, reason codes, human-readable explanation.
- `HedgePlan`: UUID, creation time, expiry, nonce, state, proposal, evidence digest, confirmation time.
- `SimulatedOrder`: side, quantity, reference price, disclosed slippage, simulated fill price, state.
- `SimulatedPosition`: opening quantity, remaining quantity, entry price, mark price, PnL, hedge ratio, expiry.
- `Receipt`: complete evidence trail, state transitions, before/after exposure, canonical digest.

### Hedge calculation

Use these conceptual calculations:

```text
spot_quantity = sample or source-labelled Spot BNB
existing_short_equivalent = absolute value of existing simulated short
target_short = spot_quantity * target_hedge_ratio
required_adjustment = target_short - existing_short_equivalent
net_exposure_before = spot_quantity - existing_short_equivalent
net_exposure_after = spot_quantity - target_short
hedge_percentage_after = target_short / spot_quantity * 100
hedge_notional = required_adjustment * perpetual_reference_price
estimated_margin = hedge_notional / leverage
```

Estimate and display:

- Opening fee.
- Projected funding over the requested duration.
- Estimated closing fee.
- A disclosed simulated slippage assumption.
- Total estimated carrying cost.

All assumptions must be visible beside the proposal.

## 8. Deterministic risk gate

An LLM may interpret and explain the request, but it may not override risk policy. Run checks in a stable order and return structured reason codes.

Required checks:

1. `KILL_SWITCH` — block when enabled.
2. `REAL_EXECUTION_DISABLED` — reject anything not explicitly simulated.
3. `MALFORMED_EVIDENCE` — required fields or units are invalid.
4. `UNVERIFIED_SOURCE` — connected-data claims lack source evidence.
5. `STALE_DATA` — source information exceeds configured freshness.
6. `SYMBOL_NOT_ALLOWED` — anything except BNBUSDT.
7. `INVALID_HEDGE_RATIO` — ratio outside 1–100%.
8. `OVER_HEDGE` — resulting short exceeds Spot exposure.
9. `LEVERAGE_LIMIT` — leverage above 2x.
10. `NOTIONAL_LIMIT` — below symbol minimum or above demo ceiling.
11. `FUNDING_COST_LIMIT` — projected cost exceeds configured threshold.
12. `PLAN_EXPIRED` — plan has passed its TTL.
13. `DUPLICATE_PLAN` — nonce already used.
14. `UNWIND_BOUND` — close quantity exceeds the simulated open position.

Blocked checks must explain what failed and how the user can safely correct it.

## 9. Complete product flow

### A. Inspect

Load the sample portfolio or normalized Binance MCP evidence. Show provenance and timestamp for price, funding, contract rules, Spot quantity, and any existing simulated hedge.

### B. Interpret

Support the canonical command and close variants. Normalize into a typed `HedgeIntent`. Ask for clarification only if asset, ratio, or duration is missing or contradictory.

The website does not need an embedded LLM. Implement a narrow, deterministic command interpreter for BNB hedge requests and also provide direct form controls.

### C. Propose

Generate a proposal containing:

- Spot BNB.
- Existing short.
- Required short adjustment.
- Hedge ratio.
- Duration.
- Leverage.
- Reference price.
- Estimated margin.
- Fees and projected funding.
- Net exposure before and after.
- Risk assumptions.
- Plan ID and expiry.

### D. Risk-check

Animate the ordered checks quickly and purposefully. The final decision must come from deterministic code, not animation timing or LLM prose.

### E. Confirm

Require explicit confirmation of the current `plan_id`. Generic prior consent does not count. Confirmation creates a short-lived single-use nonce.

### F. Simulate execution

1. Confirm the plan is approved, unused, and unexpired.
2. Refresh connected evidence where available.
3. Recalculate quantity and cost.
4. Rerun the risk gate.
5. Progress through `preparing`, `simulating_fill`, `recording_position`, and `completed`.
6. Apply a deterministic simulated fill from the reference price and disclosed slippage assumption.
7. Update simulated exposure.
8. Generate a receipt explicitly labelled as simulated.

### G. Monitor

Display:

- Spot BNB.
- Simulated short quantity.
- Net BNB exposure.
- Effective hedge percentage.
- Entry and current reference price.
- Simulated PnL.
- Accrued/projected funding.
- Remaining duration.
- Risk and source status.

### H. Unwind

Create a separate reduce-only unwind proposal. It may close only the remaining simulated short quantity. Require confirmation and generate a linked closing receipt.

## 10. HedgeKnight MCP server

Expose streamable HTTP MCP at `/mcp` and implement these ten coherent tools:

1. `hedgeknight_status`
2. `hedgeknight_exposure`
3. `hedgeknight_funding_cost`
4. `hedgeknight_propose_hedge`
5. `hedgeknight_evaluate_risk`
6. `hedgeknight_confirm_plan`
7. `hedgeknight_simulate_execution`
8. `hedgeknight_monitor_hedge`
9. `hedgeknight_propose_unwind`
10. `hedgeknight_receipt`

Each tool must have:

- A concise purpose-specific description.
- Strict JSON input schema.
- Strict structured output.
- Stable error codes.
- Mode and source labels.
- No hidden real-execution behavior.

The MCP server and REST API must call the same internal services.

Create `skills/hedgeknight-binance/SKILL.md` explaining the AI-host coordination order:

1. Inspect available Binance MCP tools.
2. Gather required Binance evidence.
3. Pass normalized source-labelled evidence to HedgeKnight.
4. Request a hedge proposal.
5. Evaluate risk.
6. Present the complete plan to the user.
7. Obtain explicit confirmation.
8. Simulate execution.
9. Monitor or unwind.
10. Return the receipt and limitations.

Never hard-code assumed official Binance MCP tool names into claims or documentation. Document observed names only after successful discovery.

## 11. REST and event interface

Provide a small documented API such as:

```text
GET  /health
GET  /api/status
GET  /api/exposure
GET  /api/market
POST /api/intents/parse
POST /api/plans
POST /api/plans/{plan_id}/confirm
POST /api/plans/{plan_id}/simulate
GET  /api/positions/active
POST /api/positions/{position_id}/unwind-plan
GET  /api/receipts
GET  /api/receipts/{receipt_id}
GET  /api/scenarios
POST /api/scenarios/{scenario_id}/load
GET  /api/events
```

Use SSE for short-lived proposal, risk-check, execution, and monitoring state updates. Do not introduce WebSockets unless the existing stack already uses them cleanly.

## 12. Dashboard information architecture

The first viewport must show the working product, not a marketing hero.

### Navigation

- Overview.
- Create hedge.
- Monitor.
- Receipts.
- Activity.
- Settings.

### Persistent top status

- `DEMO` mode badge.
- Data-source state.
- `SIMULATED EXECUTION` label.
- Kill-switch state.
- Last refresh timestamp.

### Overview

- Primary net exposure figure.
- Spot quantity and simulated futures quantity.
- Before/after exposure visualization.
- Active hedge status.
- Current funding and projected cost.
- One prominent `Create hedge` action.

### Create hedge

- Natural-language command field prefilled with the canonical command.
- 25%, 50%, and 100% presets.
- Duration and leverage controls.
- Proposal summary.
- Ordered risk checks.
- Exact confirmation step.

### Monitor

- Current simulated position.
- Effective hedge percentage.
- Reference price and simulated PnL.
- Remaining time.
- Source freshness.
- `Prepare unwind` action.

### Receipts

- Searchable receipt list.
- Opening/closing relationship.
- Mode and source badges.
- Expandable JSON evidence.
- Copy/download receipt.
- SHA-256 digest verification state.

### Judge controls

Provide a compact scenario selector clearly labelled `Judge demo scenarios`. It must be accessible without login.

## 13. Visual system

The product must feel professional, minimal, technical, and naturally at home beside Binance products without copying Binance branding or layouts.

- Near-black `#0B0E11` canvas.
- Graphite surfaces.
- Warm off-white primary text.
- Binance-adjacent gold `#F0B90B` used sparingly for primary actions, selected states, chart highlights, and the HedgeKnight mark.
- Green only for approved or healthy states.
- Amber for warnings.
- Red only for blocked or destructive states.
- Original HedgeKnight identity: a minimal flat 2D shield/eclipsed-moon mark with a compact wordmark and small `by Umbra` signature.
- Clear hierarchy, generous breathing room, tabular numerals, and monospaced technical evidence.
- Crisp 1px borders, modest radii, almost no shadow, and minimal gradients.
- The first viewport should have one decisive exposure number, one before/after graphic, one main action, and supporting evidence.
- Motion must explain proposal calculation, risk progression, confirmation, and exposure change.

Avoid:

- Copied Binance logos or layouts.
- Generic crypto neon.
- Glassmorphism.
- 3D coins.
- Mascots.
- Fake candlestick decoration.
- Huge marketing headlines.
- Walls of equal-weight cards.
- Noisy gradients.
- Excessive animations.
- Tiny unreadable technical text.

Optimize desktop recording at 1440px while remaining usable on mobile.

## 14. Required demo scenarios

Ship fixtures and a one-click selector for:

1. Valid 50% hedge for 24 hours — approved and simulated.
2. 10x leverage — blocked.
3. 125% hedge — blocked as over-hedged.
4. Stale market evidence — blocked.
5. Unverified connected-data source — blocked.
6. Funding cost above threshold — blocked.
7. Expired plan — blocked.
8. Duplicate simulated execution — blocked.
9. Kill switch enabled — blocked.
10. Valid reduce-only unwind — approved and simulated.

The default demo should complete in under 60 seconds without typing or login.

## 15. Receipts and evidence

Receipts must use stable canonical JSON and contain a SHA-256 digest calculated over the canonical content excluding the digest field.

Each receipt includes:

- Receipt ID.
- Plan ID.
- Parent opening/closing receipt where applicable.
- Requested command.
- Normalized intent.
- Mode and execution type.
- Source-labelled evidence with timestamps.
- Proposal calculations and assumptions.
- Ordered risk decisions.
- Confirmation timestamp.
- Simulated order and position state.
- Before/after exposure.
- Final state.
- Receipt digest.

Create `submission/evidence-manifest.json` mapping each headline claim to:

- Relevant code path.
- Demo scenario.
- Receipt or evidence example.
- Verification command.
- Real, connected, replay, or simulated classification.

This manifest must be valid JSON and easy for automated evaluation to parse.

## 16. AI-evaluator-friendly repository framing

Optimize for accurate, fast evaluation rather than keyword stuffing.

The top of `README.md` must contain:

1. HedgeKnight name, tagline, and one-sentence purpose.
2. A concise `What is real` table.
3. A concise `What is simulated` table.
4. The two-entry-point architecture diagram.
5. A 60-second end-to-end demo flow.
6. Exact Binance Agent OS dependency.
7. Reproducible quickstart.
8. Evidence instructions.
9. Limitations and risk disclosure.

Create `JUDGING.md` with:

- Problem.
- User value.
- Why an agent is necessary.
- Why Binance Agent OS is essential.
- Architecture.
- Safety model.
- Demonstrated agent workflow.
- Reproducibility.
- Originality.
- Evidence index.
- Limitations.

Create `SUBMISSION.md` with:

- 50-word description.
- 150-word description.
- X post draft.
- 60-second demo script.
- Two-minute demo script.
- Screenshot checklist.
- Public URL placeholders.
- Final submission checklist.

Do not use unsupported claims such as `first`, `only`, `fully autonomous`, `risk-free`, `guaranteed`, `live execution`, or `institutional-grade`.

## 17. Minimal smoke verification only

Do not build an enterprise test suite. Build and visually inspect the complete product first. Only after the canonical workflow works, add these fast smoke checks protecting the demo’s core claims:

- One hedge-sizing and rounding test.
- One happy-path 50% hedge test.
- One table-driven test covering blocked scenarios.
- One expired/duplicate plan test.
- One reduce-only unwind test.
- One receipt-hash verification test.
- One MCP initialization, tools-list, and representative-call smoke test.
- One frontend build or render smoke check.

Keep the suite comfortably under one minute on a normal laptop. Stop adding tests as soon as these checks pass. Do not add load testing, fuzzing, exhaustive browser matrices, coverage targets, snapshot sprawl, artificial test counts, or large integration harnesses.

Spend the saved time on interface polish, working states, evidence clarity, the demo recording, and submission quality.

## 18. Security and integrity

- Never commit secrets, OAuth tokens, passwords, private keys, cookies, or personal account identifiers.
- Never request a Binance withdrawal capability.
- Never enable real execution.
- Validate REST and MCP inputs with schemas.
- Reject non-finite numbers.
- Use decimal-safe calculations.
- Allowlists must restrict the build to BNBUSDT and Demo/connected-data modes.
- Prevent duplicate simulation of a single-use plan.
- Persist the kill switch and active simulated position.
- Keep logs secret-free.
- Fail closed when required evidence is missing, stale, malformed, or mislabelled.

## 19. Recommended implementation

Respect an existing sound stack. For a fresh repository use:

### Frontend

- Next.js with TypeScript.
- Tailwind CSS or a small tokenized CSS system.
- Recharts or lightweight SVG for the exposure visualization.
- Server-sent events for workflow progression.

### Backend

- Python 3.12.
- FastAPI.
- Pydantic schemas.
- Python `Decimal`.
- SQLite.
- Official Python MCP SDK.
- Pytest for the lean acceptance suite.

### Deployment

- Dockerfiles for frontend and backend.
- One `docker-compose.yml`.
- Caddy for HTTPS and routing.
- One persistent volume for SQLite.
- One `.env.example` containing no secrets.
- One-command local startup and one documented VPS deployment path.

Do not introduce Redis, Postgres, Celery, Kafka, Kubernetes, Terraform, or separate microservices unless they are already working in the repository and materially simplify the build.

## 20. Suggested repository structure

```text
hedgeknight/
  engine/
  risk/
  plans/
  simulation/
  monitoring/
  receipts/
  evidence/
  mcp/
  api/
  persistence/
  fixtures/
ui/
skills/hedgeknight-binance/
tests/
docs/
submission/
docker-compose.yml
Caddyfile
README.md
JUDGING.md
SUBMISSION.md
.env.example
```

Adapt physical directories to the chosen framework, but preserve these logical boundaries.

## 21. Acceptance criteria

The one-shot build is complete only when:

- A fresh clone installs using documented commands.
- Demo mode starts without secrets or accounts.
- The dashboard is visually polished and responsive.
- The canonical 50% hedge flow works end to end.
- All ten judge scenarios are selectable and produce the intended outcomes.
- The same shared engine serves REST and MCP.
- HedgeKnight MCP initializes and lists its tools.
- A representative MCP workflow works with fixture or source-labelled evidence.
- The minimal smoke checks pass without delaying product completion.
- The frontend production build passes.
- No real-money execution path is exposed.
- Every simulated state is unmistakably labelled.
- Receipts are downloadable and hash-verifiable.
- README, JUDGING, SUBMISSION, agent skill, architecture documentation, and evidence manifest exist.
- Docker Compose starts the complete local product.
- VPS deployment instructions are exact and short.
- No secrets are present in tracked files.

If official Binance MCP authorization is available, capture sanitized evidence of tool discovery and at least one public or read-only data call. A funded account and real order are not acceptance requirements.

If authorization is unavailable during the build, complete the adapter boundary and exact connection instructions, use timestamped replay data, and state the limitation plainly. Never claim the authenticated path was verified.

## 22. Required final report from Codex

When finished, report only concrete outcomes:

- What works.
- What uses real Binance-sourced information.
- What uses replay fixtures.
- What is simulated.
- Build result and minimal smoke-check result.
- Exact local launch command.
- Exact VPS deployment command or steps.
- Exact HedgeKnight MCP endpoint and connection configuration.
- Optional Binance MCP authorization steps.
- Submission documents created.
- Any honest blocker.

Do not end with a roadmap in place of a working MVP.

## 23. Copy-paste launch instruction

Use this prompt after placing this file in the repository root:

> Read `HEDGEKNIGHT_ONE_SHOT_BUILD.md` completely, then implement the complete HedgeKnight by Umbra submission in this repository. Do not stop at planning, scaffolding, explanations, or a static UI. Make sensible implementation decisions autonomously. Prioritize building and polishing the professional Binance-adjacent dashboard and complete end-to-end product flow. Complete the shared deterministic hedge engine, public Demo mode, ten judge scenarios, REST/SSE API, HedgeKnight MCP server, receipts, evidence manifest, documentation, and Docker deployment. Use real Binance MCP information only when its source can be proven; otherwise use timestamped fixtures and label them honestly. Do not require funds or expose real-money execution. Run the product, inspect the rendered interface, fix functional and visible problems, run only the minimal smoke checks and production build, and leave the repository submission-ready. Do not add extra tests, infrastructure, or abstractions once the working submission is complete.
