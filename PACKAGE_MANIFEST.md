# force-trading-system-20260904-daily

Provenance layer on the Idea Observatory + daily GitHub Action.
Capital $0. Force 4 WAIT. Registry still empty. No leftover invented.

## This drop

- Seed provenance: `origin_type` + `origin_date` + `original_observation`
- IDs `FS-NNNN`; frozen versions immutable
- `independence_kinds` recorded (causal/expression/instrument/geography) — does not replace T4
- `scripts/run_daily_research.py` + `.github/workflows/daily_research.yml`
  - regression tests
  - refresh prices/FRED/COT for locked tickers (not ITA/XAR/PPA)
  - re-run leading observables, failfast taxonomy, idea-registry status, short-n daily nulls
  - **does not** overwrite `negative_control_audit.json`
  - **does not** scan Force 4, sieve-hunt, or promote
  - commits `data/meta/*.json` with `[skip ci]`

## Do not

- Fill the registry to have something to test
- Revive F2 / scan F4
- Treat daily nulls as the locked fixture
