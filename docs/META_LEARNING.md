# Meta-learning after two residual-IR failures

Locked 2026-08-24. This document answers the interrogation *before* Force 3
prices are touched. It is the reason the engine was rewritten.

---

## 1. Factor isolation — is a Force un-tradable as long-only equities?

**Short answer:** a Force is un-tradable as a *plain long-only theme basket*.
It is not un-tradable in equities. The tradable object is the residual
spread against the absorbing sector ETFs.

### What actually failed

| Force | Identification | Result | Diagnosis |
|---|---|---|---|
| F1 MAGS+SMH+SPMO vs VOO | long-only theme vs broad benchmark | IR 0.003, β_QQQ ≈ 1.24 | Legs *are* levered Nasdaq. SMH/QQQ already absorbed the flow. |
| F2 VST+ETN+PWR vs XLU+QQQ | long-only names vs sector+tech (in-sample OLS **including intercept**) | IR 0.013 | Wrong *object*: intercept residual mechanically zeros a persistent premium. |

Sector indices (QQQ, XLU, SMH, XLV) **do** absorb the common equity flow
quickly. That is their job. Scoring `mean(legs) − SPY` or even
`mean(legs) − sectorETF` therefore measures “did we pick the sector,” not
“is there a force.”

### What is still tradable

On the **same** Force 2 tickets, the corrected object

```
r_legs,t − β_{t−1}' r_controls,t
```

(betas from the prior 60 days, intercept used only to estimate β, **not**
subtracted from traded PnL; dates = intersection of all names) produced
full-sample OOS IR **0.52**, placebo −0.011, β_QQQ 0.66, β_XLU 0.44.

| Window | n | OOS hedged IR |
|---|---|---|
| 2016-12-30 → 2026-08-24 | 2462 | **0.52** |
| 2017–2019 | 766 | 0.19 |
| 2020–2021 | 513 | 0.41 |
| 2022–2023 | 509 | 1.38 |
| 2024–2026 | 673 | 0.34 |

That number **would pass** IR ≥ 0.40. Strength is concentrated in 2022–23.

### Walk-forward + costs (2026-08-25, same tickets)

| Metric | Value |
|---|---|
| Gross OOS IR | 0.520 |
| Net IR @ 5 bp one-way | **0.487** |
| Net IR @ 10 bp | 0.454 |
| Placebo IR | −0.011 |
| Mean β_XLU / β_QQQ | 0.44 / 0.66 |
| IR excluding 2022–23 | 0.317 |
| 2017–19 / 20–21 / 22–23 / 24–26 | 0.19 / 0.41 / **1.38** / 0.34 |

Hard gates all pass after costs. Soft fail: **2022–23 concentration**.
Advisory verdict: **KEEP_PAUSED_SOFT_FAIL**. Capital $0. Not Option-B.

### Law

1. Long-only theme ETFs are how F1/F2 failed. They are forbidden as a
   promotion series.
2. The tradable object is always the residual *spread*: long legs, short
   lagged-β controls. Empty controls are rejected, not scored.
3. If a correctly neutralized residual has IR ≈ 0, the force **is already
   inside the sector ETF**. That is a valid kill of that identification —
   not proof that forces cannot live in equities, and not a license to
   swap tickers.

---

## 2. Alternative signatures — do we need non-equity leading clocks?

**Short answer:** yes as a *veto / timing* layer. Never as a substitute
that promotes a failing residual.

Price is a lagging clock for a structural force. Patents, legislation, and
credit can show the force *before* the sector ETF has finished absorbing
it. That is useful. It is not a trade in this mandate.

### Clock roles (locked)

| Clock | Role | May promote a failing residual? | May veto a passing residual? |
|---|---|---|---|
| 1. Price residual (OOS hedged) | **the only promotion series** | — | — |
| 2. Leading (patents, legislation, credit, real rates, expenditure) | confirmation / opposition | **no** | **yes**, once wired |
| 3. Naming | confirmation | no | yes, once wired |
| 4. Joint shift | timing | no | yes, once wired |

A leading clock with no residual is a story. A residual with a violently
opposed leading clock (e.g. hospital HY blowing out while the longevity
spread “passes”) is a veto. NaN / unwired clocks neither veto nor
promote.

### Force 3 leading-clock slots (registered, unwired)

- `real_10y_yield` — duration of longevity cash flows
- `health_expenditure` — CMS / FRED spend
- `patent_filings` — USPTO longevity / senolytic / metabolic
- `legislation` — CMS Medicare Advantage rates, IRA drug pricing
- `credit_spreads` — hospital / provider HY vs IG

Stubs return None today. Wiring them does **not** wait on the Force 3
price scan, but the scan itself is still locked until this specification
is acknowledged.

---

## Engine correction (same day, not a new basket)

F1/F2 Phase A scored **in-sample OLS residuals including the intercept**.
A persistent premium is absorbed by that intercept, so residual IR ≈ 0
*by construction*. That is the wrong tradable object.

The engine now scores the **out-of-sample hedged portfolio return**
`r_legs,t − β_{t−1}' r_controls,t`. Dates are the **intersection** of all
legs and controls (no silent pad of missing names).

`force_learning.data.panel.residual_ols` is retired and delegates to
`force_engine.neutralize`. The only evaluation entry is
`force_engine.pipeline.evaluate_candidate`, which **neutralizes first**
and refuses unmarked / long-only baskets.

Force 3 remains locked independently and is **not scanned** in this cycle.
