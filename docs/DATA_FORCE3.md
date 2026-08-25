# Force 3 Phase A — Longevity / demographic-healthcare shifts

**Locked 2026-08-24 before any scan.** F1 and F2 are paused. Option-B fishing is forbidden.

## One-sentence definition

Longevity / demographic-healthcare is a demand-side force: an aging
population's willingness-to-pay for longer healthspan (providers, devices,
care delivery) is only loosely coupled to biotech R&D success, so
IHF+IHI+XHS should retain residual return after neutralizing the absorbing
healthcare factor (XLV) and the biotech lottery (XBI).

## Why this identification (meta-learning)

F1/F2 scored long-only theme names vs a related sector ETF. Those names *are*
the ETF. Force 3’s claim is specifically **demand vs science**: providers/devices/
services should not collapse when biotech does, and should not be identical to XLV.

If OLS vs XLV+XBI leaves IR ≈ 0, the demand/science split is already priced.
That is a valid kill, not a reason to swap in UNH or ARKG.

Leading clocks (patents, legislation, credit, real 10y, health spend) are
**veto-only**. They cannot promote a failing residual.

## Ticket group (locked)

| Role | Tickers | Why |
|---|---|---|
| Residual legs (EW) | IHF, IHI, XHS | Providers, devices, services — volume/WTP, not drug discovery |
| OLS controls | XLV, XBI | Absorbing healthcare factor + biotech lottery |
| Secondary | IBB | Alt biotech |
| Diagnostic | SPY, TLT | Market beta leftover; duration of long-dated cash flows |

**Tradable object:** residual spread (long legs, short β-weighted XLV+XBI). Never long-only.

## Pre-registered gate (do not move after seeing results)

- Rolling 60d OOS hedged residual of EW(IHF, IHI, XHS) on [XLV, XBI]
  (`r_legs,t − β_{t−1}' r_controls,t`; intercept not subtracted)
- Full-sample annualized IR ≥ **0.40**
- Sign-randomization placebo IR < **0.15**
- \|mean β_XLV\| < **0.80** and \|mean β_XBI\| < **0.80**
- Overlap ≥ **8 years**
- Phase-conditional IR is **diagnostic only** (cannot promote)
- Leading clocks are **veto-only once wired**; they cannot promote
- Fail → pause Force 3, no Option-B. Capital stays $0. Trump Account = SPYM.

## Do not run the scan until this lock is acknowledged

```
PYTHONPATH=. python scripts/test_neutralizer.py          # architecture test (no Force 3 prices)
FORCE3_LOCK_ACK=1 PYTHONPATH=. python scripts/phase_a_force3.py   # live scan — only after lock
```
