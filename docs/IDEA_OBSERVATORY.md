# Idea Observatory — Explorer / Gatekeeper

Locked 2026-09-04 with FORCE_PROTOCOL_v1.0.

```
Explorer → Gatekeeper → T0–T4 FREEZE → T5 instruments → Prosecutor → Case Against
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

## States

| State | Folder | Tickers | Question |
|---|---|---|---|
| Seed | `force_ideas/seeds/` | forbidden | Is this a mechanism? |
| Hypothesis | `force_ideas/hypotheses/` | forbidden | T0–T4 specified? |
| Frozen | `force_ideas/frozen/` + `config/hypotheses/` | still empty until `attach_instruments` | Prosecutor may run |
| Rejected | `force_ideas/rejected/` | — | cousin / ticker / quota |
| Refined | `force_ideas/refined/` | — | new id only |

`origin_type` is required: contradiction, physical_constraint, institutional_friction, demographic, technology_second_order, policy, academic_mechanism, measurement_discontinuity, human_observation, other.

## Commands

```
PYTHONPATH=. python scripts/test_idea_registry.py
PYTHONPATH=. python scripts/run_idea_registry.py
PYTHONPATH=. python scripts/run_idea_registry.py --file force_ideas/_SEED_TEMPLATE.yaml
```

`--promote` and `--scan-force4` exit 2.

This package does **not** invent a leftover. The registry is empty on purpose.
