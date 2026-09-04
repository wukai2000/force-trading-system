# Force Engine — neutralize before evaluate

Governing protocol: [`docs/RESEARCH_PROTOCOL.md`](RESEARCH_PROTOCOL.md)
(locked 2026-09-01). Residualization is **falsification, not identification**.

```
YAML spec (legs, controls, gate, clocks)
        │
        ├─ T0–T4 freeze required for new force_ids
        │    (grandfathered F1/F2/F3 skip; WAIT tickers refused)
        ▼
force_engine.pipeline.evaluate_candidate
        │
        ├─ reject if tradable ≠ residual_spread
        ├─ reject if controls empty
        ├─ reject if new force_id has no complete freeze + T5 instruments
        ├─ reject WAIT / ITA/XAR/PPA/XLI
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
        │  catalog: config/leading_observables.yaml (T2 / veto; not s_t)

        ▼
GateResult  PROMOTE_CANDIDATE | FAIL_GATE | VETO_LEADING_CLOCK
```

Raw long-only baskets never enter `evaluate_neutralized`. The engine will
not infer a score from prices when no `NeutralizedPanel` is supplied.
Paused / falsified forces emit intensity 0.

Trading engine will only propose `RESIDUAL_SPREAD` with hedge weights,
quantity 0, until paper is authorized. Trump Account is not in this path.

## Research diagnostics (not in the promotion path)

Null A (sign-null percentile / empirical p), Null B (block bootstrap at
5 / 21 / 60), Null 1 (L2 label permutation, occupancy + run-length), and
the two concentration stats live in
`force_engine.false_discovery`. They **cannot promote** and they cannot
loosen `config/multilayer_gate.yaml`. L2 `{complacency, normal, stress}`
labels condition residual IR. They are not a timing signal `s_t`. HMM /
`position_scale` maps are refused.

Canonical **research** output is `force_engine.evidence.EvidenceRecord`
(FORCE_PROTOCOL_v1.0). Evidence / Veto / Promotion are separate.
Promotion is always `NOT_PERMITTED`. `evaluate_candidate` remains the
gate path for freeze/synthetic tests and still cannot auto-promote.


F1 / F2 / F3 are `research_role: negative_control`. Run:

```
PYTHONPATH=. python scripts/run_negative_control_audit.py
PYTHONPATH=. python scripts/run_regime_label_null.py
PYTHONPATH=. python scripts/test_negative_control_contract.py
PYTHONPATH=. python scripts/run_evidence_record.py
```


If that report says **F2 → PASS**, distrust the framework — do not un-pause.
Force 4 remains WAIT. Capital $0.

Phase C T0–T4 freeze guard is in `force_engine/freeze.py` (this package).
T5 instruments attach only after freeze_complete. Mechanism-absence kill
when a *named leading* series exists is still queued — this is not a
ClockBus expansion and not a Force 4 scan.
