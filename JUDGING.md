# Judging HedgeKnight

## Problem and user value

A holder who wants to keep Spot BNB but temporarily reduce downside sensitivity must otherwise size a futures hedge, inspect contract rules and funding, estimate margin and costs, enforce safety limits, monitor the position, and unwind it correctly. HedgeKnight packages that bounded job into one explainable operation while leaving the user's underlying asset untouched.

## Why an agent is necessary

The task spans natural-language intent, changing evidence, deterministic calculations, explicit consent, stateful execution, monitoring, and a later unwind. The agent coordinates those stages and explains them; deterministic code remains authoritative for risk.

## Why Binance Agent OS is essential

Official Binance MCP is the evidence boundary for market, funding, symbol-rule, and read-only account facts. HedgeKnight normalizes those observed reads and adds the protection-specific policy and lifecycle that Binance evidence alone does not provide. Missing connected evidence fails closed.

## Architecture and safety

Next.js calls a FastAPI REST/SSE surface. A supported AI host calls official Binance MCP and HedgeKnight's streamable HTTP MCP. Both HedgeKnight entry points share one Decimal engine and SQLite state. Fourteen ordered checks cover execution mode, evidence, source verification, freshness, symbol, ratio, over-hedging, leverage, notional, funding, expiry, duplicate use, kill switch, and unwind bounds. Plans expire and are single-use. There is no live-order function.

## Demonstrated workflow

Run the canonical 50% scenario, inspect its 5.000 BNB adjustment and cost assumptions, confirm its exact plan ID, simulate, monitor 5.000 BNB net exposure, inspect the digest receipt, and perform the linked reduce-only unwind. Then load the nine safety scenarios from the judge selector.

## Reproducibility and evidence

Use the README quickstart, `pytest -q`, and `npm --prefix ui run build`. The machine-readable index is `submission/evidence-manifest.json`; each dashboard receipt exposes canonical JSON and its SHA-256 digest.

## Originality

HedgeKnight is a protection workflow rather than a signal or price-prediction bot. Its distinctive mechanism is the combination of source-labelled evidence, deterministic exposure compression, exact expiring consent, bounded simulation, and linked receipts across open and unwind.

## Limitations

All financial actions are simulated. Market and account values come from verified official Binance MCP reads. Order execution is not wired and remains unavailable.
