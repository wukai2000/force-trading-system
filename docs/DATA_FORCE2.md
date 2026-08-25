# Force 2 Phase A — Energy × AI power coupling

**Locked 2026-08-24 before first scan.** Force 1 (MAGS+SMH+SPMO vs VOO/QQQ) is
falsified (clean IR 0.003). Option B (MU/HBM vs SMH) was **rejected** to avoid
post-hoc specification search.

## One-sentence definition

Reliable, scalable electric power coupled to AI computation demand produces
residual outperformance of AI-exposed generation and grid names versus generic
utilities **and** versus broad tech.

## Ticket group

| Role | Tickers | Why |
|---|---|---|
| Residual legs (EW) | VST, ETN, PWR | AI-load generation, electrical equipment, grid build; ≥8y history |
| OLS controls | XLU, QQQ | Strip generic-utility premium and tech/AI beta |
| Secondary / leading | CEG | Nuclear + hyperscaler PPAs; history from 2022 only |
| Diagnostic | XLE | Flag energy-cycle contamination (not in promotion gate) |

## Pre-registered gate (do not move after seeing results)

- Rolling 60-day OLS residual of EW(VST, ETN, PWR) on [XLU, QQQ]
- Full-sample annualized IR ≥ **0.40**
- Time-shuffle placebo IR < **0.15**
- \|mean β_QQQ\| < **0.80** (kill stealth tech-beta, Force 1 failure mode)
- Overlapping history ≥ **8 years**
- Capital: **none**. Trump Account stays SPYM. Experimental $3k untouched.
- Sandbox: pure Python simulator only.

## Phase detector

Reuse Force-1 **Aug-22** detector (slope_z of 20d residual mean + vol_z),
**not** the original v0 absolute z>0.4 detector that produced 100% catch-up.
Thresholds are sample-relative z-scores so they transfer without Force-2-specific
retuning.

## 4 clocks (unchanged structure)

1. Ticket-group OLS residual
2. Leading indicator (CEG vs the 3-leg basket)
3. Naming cues (data-center power / nuclear PPA / grid interconnect)
4. Major-move joint shift (default 4-week lead-lag)

## Run

```
PYTHONPATH=. python scripts/phase_a_force2.py
```

## Scan result (2026-08-24, AFTER the gate was locked)

- Sample: 2016-12-29 → 2026-08-24 (2,463 OLS days, 9.65y)
- Clean IR: **0.013** → **FAIL_GATE** (required ≥ 0.40)
- Sign-randomization placebo IR: −0.025
- Mean β_QQQ = 0.61, mean β_XLU = 0.42
- **Paused. Do not iterate legs.** Force 3 is next, not this cycle.
