# PASS-0 — in-repo run 2026-09-15

Sidecar lab. Not a Force. Does not amend BR-0001. HOU-1 closed.
Spec: `force_ideas/inventory/pass0.yaml`. Consolidation: `docs/MEMO_PASS0_CONSOLIDATION.md`.

**Decision: HOLD.** Gate 6 nats not moved. F1–F3 not triggered.

| World | G2 | G1 | mean Δℓ(M2−M1) | mean Δℓ(M1−M0) |
|---|---|---|---:|---:|
| A first-order T=1500 R=80 | 0/80 | 1.00 | −2.78 | +103.3 |
| B modular order-2 T=1500 R=80 | 80/80 | 0.00 | +170.4 | −0.98 |
| C short first-order T=400 R=200 | 0/200 | 0.355 | −2.70 | +5.01 |

Naive collapse recoding: alt-claim **1.00** on A/B/C (n=40). **REFUSE**.
Identity-only orders ≤4: protected alt-claim **0** on A and C; **1.00** on B (true recovery).

`master_seed=20260915`. Split 50/25/25. Laplace α=1. Total protected nats.
Artifacts: `artifacts/pass0_result.json`, `artifacts/pass0_ladder_replicates.csv`.
