# HedgeKnight — by Umbra

**AI-powered portfolio hedging through Binance Agent OS.** HedgeKnight turns a natural-language protection request into a calculated, risk-checked, confirmed, monitored, and receipted simulated BNB hedge without requiring the user to sell the underlying asset.

| What is real | Evidence |
|---|---|
| Decimal hedge sizing, costs, and ordered risk policy | `hedgeknight/engine.py` |
| Expiring single-use plans, SQLite state, SHA-256 receipts | API responses and receipt downloads |
| REST, SSE, and ten MCP tools over one shared engine | `hedgeknight/api.py` |
| Public dashboard and ten judge scenarios | `ui/app/page.tsx` |

| What is simulated or replayed | Label |
|---|---|
| BNB market snapshot | Timestamped Binance public market replay fixture |
| Portfolio, transfer, fill, position, PnL, funding accrual, unwind | `DEMO — SIMULATED EXECUTION` |
| Official Binance MCP connected path | Adapter boundary only; authorization was unavailable during this build |

```text
Judge browser → Next.js dashboard → FastAPI REST/SSE ┐
                                                     ├→ shared engine → SQLite receipts
AI client → official Binance MCP + HedgeKnight MCP ──┘
```

## 60-second demo

Open `Create hedge`, keep the prefilled “I hold 10 BNB. Hedge 50% of my exposure for 24 hours,” select 50%, 24 hours, and 2×, then calculate. Inspect the exact 5.000 BNB adjustment, costs, source labels, and ordered risk checks. Confirm the exact plan, simulate it, inspect the monitor, open the receipt, and prepare the reduce-only unwind. The Judge demo scenarios reproduce every required blocked state without login.

## Binance Agent OS dependency

The AI host is the coordinator. Official Binance MCP provides discoverable, source-labelled market, funding, symbol-rule, and optional read-only account evidence. HedgeKnight MCP provides deterministic portfolio-protection intelligence and simulation. No official Binance MCP tool name is assumed because authorization and discovery were unavailable during this build.

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

HedgeKnight does not predict price, promise profit, or protect against every loss. This submission cannot place real orders. Slippage, fees, funding, position, PnL, and unwind are simulated. Replay evidence can become stale; connected evidence must include an observed official Binance MCP source tool and retrieval time or the risk gate blocks it.
