# Discovery sieve (2026-08-31)

Literature models are a **spanning sieve**, not a ticket factory.

F1–F3 died as sector-absorbed or path-concentrated residuals. The 18-row
table mostly names kill layers already in the gate. Wiring those names as
`map_key: defense_sovereign_capacity` always emitted ITA/XAR/PPA. That is
the same narrative-to-ticket leap as MAGS+SMH.

## Loop

```
industry/candidate panel
    → L1 lagged-β vs market (+ optional extra controls)
    → neighbor vs paused F1/F2/F3 residuals
    → concentration placebo (mean |IR| of sign-randomized copies
      staying ≥40% of observed |IR| is a kill)
    → leftover IR ≥ 0.40 and |β| < 0.80
    → SIEVE_KEEP (hypothesis only)
    → pipeline.evaluate_candidate is the only promotion path
```

Non-price series (EPU, patents, GPR) may **rank or veto** a leftover.
They may not pick legs.

## Placebo (concentration, not raw 0.15)

IR is order-invariant. Sign-randomization of any T-day series has
E[|IR|] ≈ √(2/π)·√(252/T) ≈ 0.25 at 8y, so a raw `p_ir < 0.15` lock
would reject every 8y residual, including genuine distributed alpha.

Locked intent from the F2 exhibit (clean 0.725 / placebo 0.325):

```
fail if p_ir ≥ 0.15 AND p_ir / |IR| ≥ 0.40
```

Distributed planted drift (IR ~ 3, frac ~ 0.10) passes. A handful of
outlier days (F2-class) fails. PLACEBO_RELAX / SKIP_PLACEBO / RELAX_GATE
are refused.

## Neighbor (clone detector)

Leftover IR of a linear combo of paused residuals plus iid noise sits on
the same sampling floor (~0.44 at T≈900). `leftover IR ≥ 0.40` alone
cannot detect a clone. Neighbor independence therefore requires leftover
IR ≥ 0.40 **and** the leftover surviving concentration placebo.
`span_r2` is a diagnostic (how much candidate variance paused residuals
explain); it is not a hard kill, so a real overlay drift on top of a
paused force can still show leftover IR.

Naive calendar-day indexes fix Yahoo 14:30 vs midnight residual CSVs
(previously `n_days=0` with `aligned_paused=2`).

## Bugs fixed in this package

| Bug | Fix |
|---|---|
| Placebo was signed-mean of shuffled IR (concentrates at 0) | mean **\|IR\|** of sign-randomized copies |
| Raw `p_ir < 0.15` rejects every 8y residual | concentration kill: `p_ir ≥ 0.15 AND p_ir/\|IR\| ≥ 0.40` |
| Neighbor leftover IR of a clone sits on the sampling floor | leftover must also survive concentration placebo |
| Neighbor `n_days=0` with `aligned_paused=2` | naive calendar-day index align (14:30 vs midnight) |
| `time_shuffle_ir == observed_ir` | documented as order-invariant; block bootstrap + concentration share |
| GPR URLs were invented; synthetic cache claimed "verified" | real Iacoviello `.xls`; synthetic only if `FORCE_GPR_SYNTHETIC=1` |
| `simulate_p_factor` / `simulate_gpr` hardcoded defense tickets | `map_key=None` |
| PIT default scanned ITA/XAR/PPA | default WAIT; `--research-wait-sketch` required |
| PIT scored `open` when CSVs used lowercase `close` | `pick_close_column` — never fall back to open/volume |
| Neighbor of F2 against stored F2 is a self-test | `paused_excluding_legs` drops overlapping tickets |

## Commands

```
PYTHONPATH=. python scripts/test_neutralizer.py
PYTHONPATH=. python scripts/test_discovery_sieve.py
PYTHONPATH=. python scripts/run_panel_sieve.py
PYTHONPATH=. python scripts/run_literature_hypothesis_sim.py
PYTHONPATH=. python scripts/historical_point_in_time_sim.py
PYTHONPATH=. python scripts/test_l4_wire.py
```

Do not scan Force 4. Capital $0. Trump Account = SPYM.
