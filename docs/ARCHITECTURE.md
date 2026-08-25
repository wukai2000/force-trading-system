# Force Engine — neutralize before evaluate

```
YAML spec (legs, controls, gate, clocks)
        │
        ▼
force_engine.pipeline.evaluate_candidate
        │
        ├─ reject if tradable ≠ residual_spread
        ├─ reject if controls empty
        ▼
force_engine.neutralize.neutralize_prices
        │  r_legs,t − β_{t−1}' r_controls,t
        │  β from prior lookback, intercept NOT subtracted
        ▼
force_engine.evaluate.evaluate_neutralized(..., neutralized=True)
        │  IR / placebo / |β| / overlap
        │  raw basket IR attached as DIAGNOSTIC only
        ▼
force_engine.clocks.ClockBus.veto_if_leading_contradicts
        │  leading may veto a PASS; cannot rescue a FAIL
        ▼
GateResult  PROMOTE_CANDIDATE | FAIL_GATE | VETO_LEADING_CLOCK
```

Raw long-only baskets never enter `evaluate_neutralized`. The engine will
not infer a score from prices when no `NeutralizedPanel` is supplied.
Paused / falsified forces emit intensity 0.

Trading engine will only propose `RESIDUAL_SPREAD` with hedge weights,
quantity 0, until paper is authorized. Trump Account is not in this path.
