# Idea Observatory — Explorer / Gatekeeper

Locked 2026-09-04 with FORCE_PROTOCOL_v1.0. Provenance layer 2026-09-04.

```
WORLD → OBSERVATION → SEED → PROVENANCE → SCREEN → T0–T4 FREEZE → T5 → Prosecutor → Case Against
```


Not:

```
Explorer → Tester → tweak → tester → tweak
```

The Explorer is allowed to be wrong. The Prosecutor is not allowed to be helpful.
Neither allocates capital.

## Locked decisions

1. Maximum **8** seeds, **no minimum**. Zero is `NO_RESULT` = success.
2. T0–T4 remain the freeze boundary. **T4 independence is mandatory.**
3. No tickers until after freeze.
4. No F1/F2/F3/F4 cousins (hard-ban neighborhoods in `force_ideas/registry.yaml`).
5. No strategy / backtest-derived ideas. No IR/Sharpe on a seed.
6. AI may draft mechanisms; it may not evaluate returns or pick instruments.
7. Rebuttal is `force_ideas/_CASE_AGAINST.md`, not a model.
8. Refinement = **new** `hypothesis_id`. Never overwrite frozen.
9. Verification = a **pre-named** independent dimension. Not a new lookback.
10. One frozen hypothesis at a time.
11. Independent ≠ novel. T4 asks: independent of *our* prior Forces, not “unpublished.”
12. Capital $0. Promotion `NOT_PERMITTED`. Force 4 WAIT.
13. Provenance required: `origin_type`, `origin_date`, `original_observation`.
14. IDs are `FS-NNNN`; frozen versions are immutable.
15. Daily GitHub Action refreshes locked sources and diagnostic pipelines. It does not scan, promote, or overwrite the 5k fixture.


## States

| State | Folder | Tickers | Question |
|---|---|---|---|
| Seed | `force_ideas/seeds/` | forbidden | Is this a mechanism? |
| Hypothesis | `force_ideas/hypotheses/` | forbidden | T0–T4 specified? |
| Frozen | `force_ideas/frozen/` | still empty until `attach_instruments` | Prosecutor may run |
| Rejected | `force_ideas/rejected/` | — | cousin / ticker / quota |
| Refined | `force_ideas/refined/` | — | new version id only |
| Verified | `force_ideas/verified/` | — | pre-named independent dimension |

`origin_type` + `origin_date` + `original_observation` are required. `independence_kinds` (causal / expression / instrument / geography) are recorded; they do **not** replace T4’s two kinds.


## Commands

```
PYTHONPATH=. python scripts/test_idea_registry.py
PYTHONPATH=. python scripts/run_idea_registry.py
PYTHONPATH=. python scripts/run_daily_research.py --skip-fetch --skip-nulls
PYTHONPATH=. python scripts/run_idea_registry.py --file force_ideas/_SEED_TEMPLATE.yaml

```

`--promote` and `--scan-force4` exit 2.

## FS-0001 (2026-09-05)

**Demand expansion after cost collapse** — not “Jevons” as a label, not F2.

T0: when unit cost of a capability falls sharply, aggregate demand for the underlying resource can rise because new applications become viable.

Admitted as seed + hypothesis. T0–T4 freeze_complete with **tickers empty**. T5 not attached. Prosecutor not run.

Verification (pre-named): same signed leading relationship in another geography **or** a second resource class. A cousin ETF or a new lookback is not verification.

Failure: ~50% unit-cost drop then net *decrease* in aggregate use in a mature unconstrained market.

**T5 status: blocked.** Lighting data contract frozen (`force_ideas/data_contracts/FS-0001-lighting-v1.yaml`). Primary geography = IEA multi-country; second = EU aggregate. Observatory reports **NO_RESULT** until IEA series are actually wired. A freight FRED overlay (CASSEXP / RAILFRTINTERMODAL / TSIFRHT) is **rejected** as a v1 mutation. Switching to freight/compute/water after seeing lighting data would be FS-0001 v2, not a rescue.

`attach_instruments(FS-0001)` is refused until DATA_READY. Prosecutor still false. Capital $0.


