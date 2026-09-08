# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Delegated by the user to the build specification's recommendation: Next.js with TypeScript and tokenized CSS for the dashboard; Python FastAPI, Pydantic, Decimal arithmetic, SQLite, and the Python MCP SDK for the shared service; Docker Compose and Caddy for deployment.

## Users

The primary user is a BNB holder who wants to retain Spot BNB while temporarily reducing exposure to a market decline. Hackathon judges are a second audience: they need to complete and verify the canonical protection workflow in under 60 seconds without an account, credentials, funds, or login.

## Product Purpose

HedgeKnight turns a natural-language protection request into a calculated, risk-checked, confirmed, simulated, monitored, and receipted BNB perpetual hedge. Success means a user can understand the before/after exposure and costs, pass deterministic safety checks, explicitly confirm an expiring plan, simulate the lifecycle, monitor it, and perform a bounded reduce-only unwind.

## Positioning

HedgeKnight is a portfolio-protection agent rather than a price-prediction bot. An AI host coordinates official Binance MCP evidence with HedgeKnight's deterministic sizing, policy, plan lifecycle, simulation, monitoring, and tamper-evident receipts.

## Operating Context

The connected mode requires a supported AI client to gather official Binance MCP evidence and pass source-labelled market, balance, and position reads to HedgeKnight. There is no replay fallback. All financial actions remain simulated. The canonical command is: “I hold 10 BNB. Hedge 50% of my exposure for 24 hours.”

## Capabilities and Constraints

The submission supports BNB and BNBUSDT only, hedge ratios from 1–100%, leverage up to 2x, duration presets from 4 hours to 7 days, deterministic ordered risk checks, expiring single-use plans, simulated fills and positions, monitoring, reduce-only unwind, a persisted kill switch, SHA-256 receipts, ten judge scenarios, REST/SSE, and eleven HedgeKnight MCP tools over one shared engine. It never enables real-money execution or stores Binance trading credentials. Connected and simulated evidence must remain visibly distinct.

## Brand Commitments

The product is “HedgeKnight — by Umbra” with the tagline “AI-powered portfolio hedging through Binance Agent OS.” Its identity uses a minimal shield/eclipsed-moon mark and a professional, minimal, technical voice. It must feel at home beside Binance products without copying Binance branding or layouts.

## Evidence on Hand

The complete original product and submission specification is in `HEDGEKNIGHT_ONE_SHOT_BUILD.md`. Authenticated Binance MCP discovery is now available and the connected adapter must use only observed read-tool names. It must not fabricate testimonials, customer claims, market performance, or live execution.

## Product Principles

- Make every simulated action unmistakable and every data source inspectable.
- Keep deterministic risk policy authoritative over language interpretation.
- Require explicit, exact, expiring confirmation before simulation.
- Prove the complete workflow through reproducible receipts and judge scenarios.
- Preserve one shared engine across the browser API and MCP entry point.

## Accessibility & Inclusion

The responsive dashboard must remain keyboard usable, provide visible focus and readable contrast, respect reduced-motion preferences, and expose status through text rather than color alone.
