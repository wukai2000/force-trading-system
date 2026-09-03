# Force Trading System

Unique force-based trading system built around persistent, under-noticed structural forces.

**Current phase**: Force 1 falsified, Force 2 paused (placebo fail + live last-60 L2 IR −1.05). Force 3 FAIL_GATE. Force 4 **wait / not locked**.
**Capital**: Experimental $3k unused; Trump Account stays passive in SPYM.
**Discovery (2026-08-31):** panel sieve vs paused residuals. Literature models do not pick tickets.
**Protocol (2026-09-01):** residualization is falsification, not identification. F1–F3 are negative controls. New leftovers need a T0–T4 freeze before tickers. See `docs/RESEARCH_PROTOCOL.md`.


## Architecture (four core components)

```
force_learning/          # observation → claims → laws; experiments
force_engine/            # neutralization BEFORE scoring
  ├── pipeline.py        # only evaluation entry
  ├── neutralize.py      # OOS hedged residual spread (required)
  ├── evaluate.py        # gate; concentration placebo on sign-randomized |IR|
  ├── sieve.py           # leftover vs market + paused F1/F2/F3 (finder)
  ├── literature.py      # academic models as hypothesis simulators (no ticket map)
  ├── discovery.py       # writes YAML sketches; cannot promote
  ├── neighbor.py        # spanning test vs paused F1/F2/F3 (naive-day align)
  ├── false_discovery.py # Null A/B + Null 1 (label permutation); time_shuffle/DSR legacy

  ├── freeze.py          # T0–T4 provenance; evaluate refused until complete
  ├── leading_observables.py  # T2 FRED catalog; veto-only; IR(s,r) refused
  ├── clocks.py          # 4 clocks + L4 GPR veto-only (real Iacoviello files)
  ├── layers.py          # L2 vol/credit, L3 breadth
  ├── loader.py          # config/force*.yaml
  └── engine.py          # suggestions only from neutralized panels
trading_engine/          # policies
trading_interface/       # python_sim default
```

**Meta-rule (2026-08-24):** the tradable object is the residual spread (long legs, short β-weighted controls). Long-only theme ETFs are how F1/F2 failed. See `docs/META_LEARNING.md`.

**Literature firewall (2026-08-29):** academic models generate hypotheses; the multi-layer gate kills disguised beta. See `docs/LITERATURE_MAP.md`.

**Sieve (2026-08-31):** do not start from a 3-name ETF story. A unique force is whatever is **not spanned** by market + paused F1/F2/F3 residuals. See `docs/DISCOVERY_SIEVE.md`.

**Research protocol (2026-09-01, Null 1 2026-09-02):** a Force is a pre-specified economic mechanism. Null A/B/1 cannot promote. Phase B: F1–F3 reject as negative controls (attractive F2 OOS IR 0.593 still CONCENTRATION_FAIL). L2 labels condition; they do not size. New leftovers need T0–T4 freeze before tickers. Force 4 WAIT. See `docs/RESEARCH_PROTOCOL.md`.


## Force registry
1. AI Infra / Memory — **falsified / paused** (IR 0.003)
2. Energy × AI power — **paused** (placebo 0.325; not funded)
3. Longevity / healthspan demand — **FAIL_GATE** (IHF+IHI+XHS vs XLV+XBI)
4. Defense / sovereign capacity — **sketch only, wait** (ITA+XAR+PPA vs XLI+SPY)

## Quick start

```
PYTHONPATH=. python scripts/test_neutralizer.py
PYTHONPATH=. python scripts/test_discovery_sieve.py
PYTHONPATH=. python scripts/test_null_engine.py
PYTHONPATH=. python scripts/test_freeze.py
PYTHONPATH=. python scripts/run_negative_control_audit.py
PYTHONPATH=. python scripts/run_regime_label_null.py
PYTHONPATH=. python scripts/validate_hypothesis_freeze.py
PYTHONPATH=. python scripts/test_leading_observables.py
PYTHONPATH=. python scripts/run_leading_observables.py
PYTHONPATH=. python scripts/run_literature_hypothesis_sim.py
PYTHONPATH=. python scripts/failfast_force_taxonomy.py

```

Honest PIT evaluate (cached prices; research only; close, not open):

```
PYTHONPATH=. python scripts/pit_evaluate.py --spec config/force2.yaml --as-of 2022-06-01
```

Do not run `scripts/phase_a_force3.py` until the Force 3 lock in `config/force3.yaml` is acknowledged (`FORCE3_LOCK_ACK=1`).
Do not scan Force 4. Silent default is wait. `historical_point_in_time_sim.py` refuses ITA/XAR/PPA unless `--research-wait-sketch`.

## Post-F3 status (2026-08-25)

All Phase-A forces paused (F1 falsified, F2 soft-fail then placebo kill, F3 FAIL_GATE stealth XLV).
See `docs/FORCE_TAXONOMY.md` and `docs/META_LEARNING.md`.
Fail-fast diagnostics: `PYTHONPATH=. python scripts/failfast_force_taxonomy.py`
Capital $0 / SPYM only. No Option-B.
