# force-trading-system-20260902-null1

Snapshot of `/fts` at local commit `bc79524` (2026-09-02).
Capital $0. Trump Account = SPYM. Force 4 WAIT. F1–F3 negative controls.

## What this package adds vs 20260831-discovery-sieve

| Date | Commit | Content |
|---|---|---|
| 2026-09-01 | `39cee67` | Research protocol. Null A/B + Conc A/B. Phase B audit. F2 OOS IR 0.593 still CONCENTRATION_FAIL. |
| 2026-09-01 | `0a93b2f` | T0–T4 freeze guard. `evaluate_candidate` refuses unfrozen ids. |
| 2026-09-02 | `bc79524` | Null 1: regime-label permutation. HMM / `position_scale` refused. Dwell/hysteresis sensitivity only. |

## Do not

- Scan Force 4 / ITA/XAR/PPA/XLI
- Unpause F1/F2/F3
- Treat L2 labels as a timing signal `s_t`
- Fit HMM or `REGIME_CONTROL_MAP`
- Loosen `config/multilayer_gate.yaml`

## Commands

```
PYTHONPATH=. python scripts/test_neutralizer.py
PYTHONPATH=. python scripts/test_discovery_sieve.py
PYTHONPATH=. python scripts/test_null_engine.py
PYTHONPATH=. python scripts/test_freeze.py
PYTHONPATH=. python scripts/run_negative_control_audit.py
PYTHONPATH=. python scripts/run_regime_label_null.py
PYTHONPATH=. python scripts/validate_hypothesis_freeze.py
```

## Key files

- `docs/RESEARCH_PROTOCOL.md` — source of truth
- `force_engine/false_discovery.py` — Null A/B/1
- `force_engine/freeze.py` — T0–T4 refuse-guard
- `data/meta/negative_control_audit.json`
- `data/meta/regime_label_null.json`

Prices and FRED macros are **not** in this tarball (`.gitkeep` only). Residual CSVs and meta JSON are.
