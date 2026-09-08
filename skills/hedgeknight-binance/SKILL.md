---
name: hedgeknight-binance
description: Coordinate official Binance MCP evidence with HedgeKnight's deterministic simulated BNB hedge workflow.
---

# HedgeKnight + Binance Agent OS coordination

Use this skill only for BNBUSDT portfolio-protection work. Every financial action is simulated. Never request withdrawal access or claim live execution.

1. Discover the official Binance MCP tools available in the current AI host. Do not assume or invent their names.
2. Gather BNB spot/reference price, BNB perpetual price, funding, symbol rules, retrieval time, and—only when authorized—read-only Spot BNB evidence.
3. Pass normalized evidence with value, unit, source, observed source tool, retrieval time, and verification state to HedgeKnight.
4. Call `hedgeknight_propose_hedge` with the requested ratio, duration, and leverage.
5. Call `hedgeknight_evaluate_risk`; deterministic policy is final.
6. Present quantity, before/after exposure, margin, fees, funding, slippage, evidence, plan ID, expiry, and all blocked checks.
7. Obtain explicit confirmation of that exact plan ID.
8. Call `hedgeknight_confirm_plan`, then `hedgeknight_simulate_execution`.
9. Monitor with `hedgeknight_monitor_hedge`; unwind only through `hedgeknight_propose_unwind` and the bounded reduce-only flow.
10. Return `hedgeknight_receipt`, its SHA-256 digest, source labels, and the limitations that market evidence may be connected while all financial actions remain simulated.

Stable HedgeKnight tools: `hedgeknight_status`, `hedgeknight_exposure`, `hedgeknight_funding_cost`, `hedgeknight_propose_hedge`, `hedgeknight_evaluate_risk`, `hedgeknight_confirm_plan`, `hedgeknight_simulate_execution`, `hedgeknight_monitor_hedge`, `hedgeknight_propose_unwind`, and `hedgeknight_receipt`.

