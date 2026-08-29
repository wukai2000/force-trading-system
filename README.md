# Force Trading System

Unique force-based trading system built around persistent, under-noticed structural forces.

**Current phase**: Force 1 falsified, Force 2 paused (placebo fail + live last-60 L2 IR −1.05). Force 3 FAIL_GATE. Force 4 **wait / not locked**.
**Capital**: Experimental $3k unused; Trump Account stays passive in SPYM.

## Architecture (four core components)

```
force_learning/          # observation → claims → laws; experiments
force_engine/            # neutralization BEFORE scoring
  ├── pipeline.py        # only evaluation entry
  ├── neutralize.py      # OOS hedged residual spread (required)
  ├── evaluate.py        # gate; refuses raw baskets
  ├── literature.py      # academic models as hypothesis simulators
  ├── discovery.py       # writes YAML sketches; cannot promote
  ├── neighbor.py        # spanning test vs paused F1/F2/F3
  ├── false_discovery.py # DSR / time-shuffle diagnostics (not a new gate)
  ├── clocks.py          # 4 clocks; leading veto only
  ├── layers.py          # L2 vol/credit, L3 breadth
  ├── loader.py          # config/force*.yaml
  └── engine.py          # suggestions only from neutralized panels
trading_engine/          # policies
trading_interface/       # python_sim default
```

**Meta-rule (2026-08-24):** the tradable object is the residual spread (long legs, short β-weighted controls). Long-only theme ETFs are how F1/F2 failed. See `docs/META_LEARNING.md`.

**Literature firewall (2026-08-29):** academic models generate hypotheses; the multi-layer gate kills disguised beta. See `docs/LITERATURE_MAP.md` and `docs/SIMULATION_RESEARCH_PLAN.md`.

## Force registry
1. AI Infra / Memory — **falsified / paused** (IR 0.003)
2. Energy × AI power — **paused** (placebo 0.325; not funded)
3. Longevity / healthspan demand — **FAIL_GATE** (IHF+IHI+XHS vs XLV+XBI)
4. Defense / sovereign capacity — **sketch only, wait** (ITA+XAR+PPA vs XLI+SPY)

## Quick start

```
PYTHONPATH=. python scripts/test_neutralizer.py
PYTHONPATH=. python -m force_engine.engine --demo
PYTHONPATH=. python scripts/run_literature_hypothesis_sim.py
PYTHONPATH=. python scripts/failfast_force_taxonomy.py
```

Honest PIT evaluate (cached prices; research only):

```
PYTHONPATH=. python scripts/pit_evaluate.py --spec config/force2.yaml --as-of 2022-06-01
```

Do not run `scripts/phase_a_force3.py` until the Force 3 lock in `config/force3.yaml` is acknowledged (`FORCE3_LOCK_ACK=1`).
Do not scan Force 4. Silent default is wait.

## Post-F3 status (2026-08-25)

All Phase-A forces paused (F1 falsified, F2 soft-fail then placebo kill, F3 FAIL_GATE stealth XLV).
See `docs/FORCE_TAXONOMY.md` and `docs/META_LEARNING.md`.
Fail-fast diagnostics: `PYTHONPATH=. python scripts/failfast_force_taxonomy.py`
Capital $0 / SPYM only. No Option-B.
