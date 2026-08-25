# Force 2 — Energy × AI power coupling

**Status: PAUSED** (2026-08-25 walk-forward review). Same tickets. No capital.

## One-sentence definition

Reliable, scalable electric power coupled to AI computation demand produces
residual outperformance of AI-exposed generation and grid names versus generic
utilities **and** versus broad tech.

## Ticket group (locked — not iterated)

| Role | Tickers | Why |
|---|---|---|
| Residual legs (EW) | VST, ETN, PWR | AI-load generation, electrical equipment, grid build |
| OLS controls | XLU, QQQ | Strip generic-utility and tech/AI beta |
| Secondary / leading | CEG | Nuclear + hyperscaler PPAs (short history) |
| Diagnostic | XLE | Energy-cycle contamination flag |

**Tradable object:** residual spread
`r_legs,t − β_{t−1}' r_controls,t` (60d lagged β, intercept not subtracted).

## Phase A (2026-08-24) — old metric

In-sample OLS residual **including intercept** → clean IR **0.013** → FAIL_GATE.
That object mechanically zeros a persistent premium. Paused.

## Engine-correction + walk-forward (2026-08-25)

Same tickets, corrected OOS hedged residual. Advisory only — does not un-pause.

### Full sample (2016-12-30 → 2026-08-24, n=2462, 9.65y)

| Metric | Value |
|---|---|
| Gross OOS IR | **0.520** |
| Net IR (1 bp one-way) | 0.513 |
| Net IR (5 bp one-way) | **0.487** |
| Net IR (10 bp one-way) | 0.454 |
| Sign-placebo IR | −0.011 |
| Mean β_XLU | 0.443 |
| Mean β_QQQ | 0.659 |
| Mean daily turnover | 0.073 (~18×/yr; mostly hedge β drift) |

Hard gates (IR ≥ 0.40 after 5 bp, |β| < 0.80, placebo < 0.15, ≥8y): **all pass**.

### Calendar regimes (gross)

| Window | n | IR |
|---|---|---|
| 2017–2019 | 766 | 0.190 |
| 2020–2021 | 513 | 0.413 |
| 2022–2023 | 509 | **1.382** |
| 2024–2026 | 673 | 0.342 |
| Excluding 2022–2023 | — | 0.317 |

### Annual folds (gross)

| Year | IR | Year | IR |
|---|---|---|---|
| 2017 | 0.069 | 2022 | 1.527 |
| 2018 | −0.051 | 2023 | 1.292 |
| 2019 | 0.459 | 2024 | 0.526 |
| 2020 | 0.048 | 2025 | −0.011 |
| 2021 | 0.974 | 2026 YTD | 0.588 |

### Advisory verdict

**KEEP_PAUSED_SOFT_FAIL**

- Hard fails: none
- Soft fail: 2022–23 concentration (IR > 1.0 while 2017–19 < 0.25)
- Action: leave `phase_a_failed_paused`. Capital $0. Trump Account = SPYM.

Edge survives realistic ETF costs. Regime path is real but dominated by the
AI-power boom years. Human may later un-pause with eyes open; the system will not.

## Artifacts

- `data/force2/force2_walkforward_summary.json`
- `data/force2/force2_walkforward_daily.csv`
- `data/force2/force2_walkforward_regimes.csv`
- `data/force2/force2_walkforward_annual.csv`
- `charts/force2/force2_walkforward.png`

## Run

```
PYTHONPATH=. python scripts/walkforward_force2.py
```
