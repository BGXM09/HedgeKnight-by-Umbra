# HedgeKnight — by Umbra

**AI-powered portfolio hedging through Binance Agent OS.** HedgeKnight turns a natural-language protection request into a calculated, risk-checked, confirmed, monitored, and receipted simulated BNB hedge without requiring the user to sell the underlying asset.

| What is real | Evidence |
|---|---|
| Decimal hedge sizing, costs, and ordered risk policy | `hedgeknight/engine.py` |
| Expiring single-use plans, SQLite state, SHA-256 receipts | API responses and receipt downloads |
| REST, SSE, and eleven MCP tools over one shared engine | `hedgeknight/api.py` |
| Public dashboard and ten judge scenarios | `ui/app/page.tsx` |

| What remains simulated | Label |
|---|---|
| Transfer, fill, PnL, funding accrual, unwind | `DEMO — SIMULATED EXECUTION` |
| Order placement | Disabled; no Binance order endpoint is wired |

Live BNBUSDT mark/index price, funding, symbol rules, Spot BNB balance, USDⓈ-M balance, and USDⓈ-M position are normalized from official Binance MCP read tools. The AI host calls those tools and submits their outputs to `POST /api/binance/read-snapshot`; HedgeKnight rejects missing data or unexpected tool provenance and has no replay fallback.

```text
Judge browser → Next.js dashboard → FastAPI REST/SSE ┐
                                                     ├→ shared engine → SQLite receipts
AI client → official Binance MCP + HedgeKnight MCP ──┘
```

## 60-second demo

First use a supported AI host to submit a fresh official Binance MCP read snapshot to `POST /api/binance/read-snapshot`. Then open `Create hedge`, keep the prefilled “I hold 10 BNB. Hedge 50% of my exposure for 24 hours,” select 50%, 24 hours, and 2×, and calculate. Inspect the exact adjustment, costs, source labels, and ordered risk checks. Confirm the exact plan, simulate it, inspect the monitor, open the receipt, and prepare the reduce-only unwind. The judge scenarios reproduce every required policy state without enabling order execution.

## Binance Agent OS dependency

The AI host is the coordinator. Official Binance MCP provides source-labelled market and authenticated account evidence through `futures_usds.markPrice`, `futures_usds.exchangeInformation`, `spot.getAccount`, `futures_usds.futuresAccountBalanceV3`, and `futures_usds.positionInformationV2`. HedgeKnight MCP provides deterministic portfolio-protection intelligence and simulation. Live order execution remains deliberately disconnected.

## Quickstart

```bash
python3.12 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
npm --prefix ui install
python -m hedgeknight
# another terminal
npm --prefix ui run dev
```

Open `http://localhost:3000`. The API is at `http://localhost:8000`, OpenAPI at `/docs`, SSE at `/api/events`, and streamable HTTP MCP at `http://localhost:8000/mcp`.

Run the lean checks with `pytest -q` and `npm --prefix ui run build`. Inspect `submission/evidence-manifest.json` for machine-readable claim mapping. Receipts can be downloaded from the dashboard and independently verified by hashing canonical JSON after removing `digest`.

## Deployment

On a Docker-enabled VPS, set `DOMAIN` to a DNS name pointing at the server and run:

```bash
DOMAIN=hedge.example.com docker compose up -d --build
```

Caddy provisions HTTPS, routes `/api`, `/health`, and `/mcp` to FastAPI, and routes the remaining surface to Next.js. SQLite persists in the `hedgeknight-data` volume.

## Limitations and risk disclosure

HedgeKnight does not predict price, promise profit, or protect against every loss. This submission cannot place real orders. Slippage, fees, fills, PnL, and unwind are simulated. Connected evidence must include the observed official Binance MCP tools and retrieval time or ingestion fails closed; stale evidence is blocked by the risk gate.
