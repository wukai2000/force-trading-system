# Force Trading System

Unique force-based trading system built around persistent, under-noticed structural forces.

**Current phase**: Force 1 falsified, Force 2 paused (engine-correction IR 0.52 flagged, not funded). Force 3 locked, **not yet scanned**.
**Capital**: Experimental $3k unused; Trump Account stays passive in SPYM.

## Architecture (four core components)

```
force_learning/          # observation → claims → laws; experiments
force_engine/            # neutralization BEFORE scoring
  ├── pipeline.py        # only evaluation entry
  ├── neutralize.py      # OOS hedged residual spread (required)
  ├── evaluate.py        # gate; refuses raw baskets
  ├── clocks.py          # 4 clocks; leading (patents/legislation/credit) veto only
  ├── loader.py          # config/force*.yaml
  └── engine.py          # suggestions only from neutralized panels
trading_engine/          # policies
trading_interface/       # python_sim default
```

**Meta-rule (2026-08-24):** the tradable object is the residual spread (long legs, short β-weighted controls). Long-only theme ETFs are how F1/F2 failed. See `docs/META_LEARNING.md`.

## Force registry
1. AI Infra / Memory — **falsified / paused** (IR 0.003)
2. Energy × AI power — **paused** (old IR 0.013; OOS hedged diagnostic 0.52, not un-paused)
3. Longevity / healthspan demand — **locked pre-scan** (IHF+IHI+XHS vs XLV+XBI)

## Quick start

```
PYTHONPATH=. python scripts/test_neutralizer.py
PYTHONPATH=. python -m force_engine.engine --demo
```

Do not run `scripts/phase_a_force3.py` until the Force 3 lock in `config/force3.yaml` is acknowledged (`FORCE3_LOCK_ACK=1`).

## Post-F3 status (2026-08-25)

All Phase-A forces paused (F1 falsified, F2 soft-fail concentration, F3 FAIL_GATE stealth XLV).
See `docs/FORCE_TAXONOMY.md` and `docs/META_LEARNING.md`.
Fail-fast diagnostics: `PYTHONPATH=. python scripts/failfast_force_taxonomy.py`
Capital $0 / SPYM only. No Option-B.
