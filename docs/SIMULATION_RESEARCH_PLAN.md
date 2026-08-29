# Simulation research plan (2026-08-29)

Purpose: use literature models as **hypothesis simulators**, then let the
existing multi-layer pipeline kill anything that is disguised beta.
Not a Force 4 lock. Not a scan authorization. Capital $0.

## Decision state this package does *not* change

- F1 falsified, F2 permanently paused (placebo 0.325 + last-60 L2 IR −1.05).
- F3 FAIL_GATE (stealth β_XLV, neighbor IR 0.048 vs F2).
- Placebo IR < 0.15 stays a hard kill.
- Defense ITA+XAR+PPA vs XLI+SPY remains a **sketch** in
  `config/theme_ticket_map.yaml` with `lock_status: wait`.
- Silent default remains **wait / do not scan**.

## Package delivered in this commit

| Path | Job |
|---|---|
| `docs/LITERATURE_MAP.md` | 5 original + 13 missing frameworks, mapped to layers |
| `config/literature_models.yaml` | Registry: hypothesis vs kill vs veto |
| `config/theme_ticket_map.yaml` | Frozen *research* theme→ticket sketches (not scannable) |
| `force_engine/literature.py` | All literature simulators, mock-safe |
| `force_engine/neighbor.py` | Neighbor orthogonalization vs paused residuals |
| `force_engine/false_discovery.py` | Time-shuffle + deflated-Sharpe *diagnostics* |
| `force_engine/discovery.py` | Delegates to literature; writes sketches only |
| `scripts/run_literature_hypothesis_sim.py` | Run every model; print hypotheses; no prices required |
| `scripts/pit_evaluate.py` | Honest PIT: neutralize + gate; raw IR diagnostic only |
| `scripts/historical_point_in_time_sim.py` | Multi-cutoff scout using the pipeline |

## How the loop is supposed to run

```
1. FIND      literature simulators on series truncated at T
2. MAP       theme → tickets only if the map row existed at T
             (no 2026 hindsight ticket pick)
3. EVALUATE  pipeline.evaluate_candidate on cached prices
             IS ≤ T diagnostic; OOS > T scout; full-sample gate separate
4. INVESTIGATE  regimes, L2/L3, neighbor vs F1/F2/F3, costs
5. RESEARCH  walk T across month-ends; record false-discovery rate
6. DECIDE    human lock or wait. Software never allocates.
```

A 6-month OOS window is a **scout**. It cannot satisfy `min_overlap_years: 8`
or “IR ≥ 0.35 in ≥ 2 non-shock regimes.” Scout PASS ≠ promotion.

## Near-term sequence (no capital)

### Week 1 — wire honest evaluation (this package)

- Run `scripts/run_literature_hypothesis_sim.py` (synthetic proxies OK).
- Run `scripts/pit_evaluate.py --spec config/force2.yaml` on cached prices
  as a regression test that the new runner uses neutralization.
- Do **not** treat Defense YAML as scannable.

### Week 2 — cache missing free proxies

- GPR / AI-GPR monthly CSV from Iacoviello (L4 diagnostic).
- EPU (Baker-Bloom-Davis) monthly.
- Optional: USPTO category counts for one sketch theme only.
- Keep using FRED L2 series already in `data/macro/`.

### Week 3 — research matrix, still no lock

- Month-end as-of dates 2018–2024 for *paused* F1/F2/F3 specs only
  (engine-correction / look-ahead audit, not revival).
- Same dates for Defense *sketch* under `--research-only` flag.
- Report: neutralized OOS IR, placebo, |β|, neighbor IR, GPR residual.

### Week 4+ — human fork

- (a) Explicit wait, or
- (b) Lock Force 4 tickets under the neighbor protocol already drafted
  in Daily Thinking (2026-08-28). Software will not choose (b).

## Kill list (do not do)

- Do not un-pause F2 because any new literature IR looks large.
- Do not recycle MAGS/SMH/SPMO, VST/ETN/PWR, IHF/IHI/XHS.
- Do not use QQQ as a leg.
- Do not loosen placebo after it bites.
- Do not promote from Shiller / EPU / patents / GPR alone.
- Do not treat raw EW(legs)−EW(controls) as the evaluation object.
- Do not commit Ken French / paid MediaStats as a dependency yet.

## Success criteria for the *research* loop (not for capital)

1. Every literature model has a code hook and a stated role (find / kill / veto).
2. Every candidate that reaches numbers went through `evaluate_candidate`.
3. A table of as-of dates exists under `data/meta/` with scout vs gate columns.
4. False-discovery diagnostics run when many dates are scanned.
5. Notion / README still say capital $0 and Force 4 = wait.
