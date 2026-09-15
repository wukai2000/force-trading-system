# Pass-0 consolidation — 2026-09-15

Three notes plus a PDF from an empty sandbox. One frozen spec.
Capital `$0`. Architecture unchanged. HOU-1 not opened. 6 nats not moved.

## What each note actually is

| Source | Claim | Status here |
|---|---|---|
| PDF / Pass-0 report | Ran A/B/C + collapse stress in an empty env. HOLD. | Spec to reproduce in-repo. Not yet a repo artifact until this commit. |
| Audit memo (HEAD `cf7d3b8`) | Test-0 not run; propose binary XOR B, 5k-seed C. HOLD. | Stale HEAD. Spec cousins, not a second experiment. |
| Protocol memo | Same three-world idea; C = discretized AR(1); FPR≤0.01. HOLD. | Different World C. New FPR target is a threshold edit. |

## Keep (law)

1. **Discrimination, not recovery.** World B must be a process M1 cannot absorb.
   Wave-0 `ABC` failed that. Pass-0 modular rule
   `P(X_t=(X_{t-2}+X_{t-1}+1) mod 3)=0.80` keeps it. XOR-on-binary is the
   same idea with a smaller alphabet. **Use the Pass-0 K=3 modular DGP.**
   Do not rerun ABC and call it World B.
2. **Double gate, frozen.** G2 iff protected `Δℓ(M2−M1)≥6` **and**
   `Δℓ(M2−M0)≥6`. Total nats, not per-step. The one World C near-miss
   (`+6.36` vs M1, `+4.01` vs M0) is why the M0 conjunct exists.
3. **Sign-preference is not a gate.** World A sign-preferred M2 in 33.8%
   with mean `Δℓ(M2−M1)=−1.95`. A magnitude-free rule is a false-structure
   machine.
4. **Naive recoding + raw LL is REFUSE.** Collapse-to-one-symbol has `ℓ=0`
   and wins every replicate. Forced constraint: score on a fixed observation
   alphabet, or pay a description-length term for the recoding. **Document,
   do not build a new layer.**
5. **HOU-1 / historical / EvidenceRecord: REFUSE.** Synthetic recovery is
   not historical evidence. Gate 1 is still UNRESOLVED. `next_object`
   remains `2011_nc_first_print_or_stop`.
6. **6 nats is sample-size dependent.** World C G1=0.505 at T=400,
   stay=0.50 is a power fact. Do not lower the gate to make first-order
   “show up.” Do not raise it because one near-miss existed.

## Dismiss

| Item | Why |
|---|---|
| Binary XOR as a *replacement* World B | Same scientific object as modular K=3. Pass-0 already chose K=3. |
| World C = median-split AR(1) | Different DGP family. Mixing it in is a new experiment. |
| 5,000 seeds × four n for Type I | Diagnostic cousin. Not this pass. Does not license a new FPR target. |
| FPR ≤ 0.01 as a frozen law | Threshold edit after imagining Type I. F3 is already G2 rate > 0.10. |
| 60/20/20 or 40/30/30 splits | Pass-0 froze 50/25/25. Do not restick the split. |
| Unbounded Condition 5 (N_eval>10⁴) | Search-damage point is already made at collapse (C2). |
| “Protected integrity CONTRADICTED” as a repo fact | A1-v1 was development. Pass-0 protected split was not inspected. |
| “Architecture had to become restricted” | Frozen ladder needed **nothing**. Collapse REFUSE is a procedure kill, not a new module. |
| Calling Pass-0 an EvidenceRecord / grammar recovery / AETL-E0 replication | Hard prohibitions. |
| Opening HOU-1 because HOLD ≠ REFUSE | HOLD means do not proceed to discovery. |
| Duration / unobserved-mode DGPs **this commit** | Next hostile *synthetic* pass if one happens. Not licensed to become modules. Not this run. |

## Frozen spec (this commit)

See `force_ideas/inventory/pass0.yaml`.

- Alphabet `{0,1,2}` supplied, not inferred.
- A: first-order stay=0.70 / off=0.15, T=1500, R=80. Expect M1_sufficient, G2=0.
- B: modular second-order, T=1500, R=80. Expect G2, G1≈0 (M1 blind).
- C: first-order stay=0.50 / off=0.25, T=400, R=200. Expect G2 rate low.
- Split 50 / 25 / 25 temporal. Fit train. Gate on protected only. Laplace α=1.
- master_seed `20260915`. Replicate RNG = SHA-256(`master|W|r|tag`).
- F1: A G2>0.10. F2: B G2<0.80. F3: C G2>0.10.
- Search: C1 identity M0/M1/M2; C2 + collapse (naive, expected REFUSE);
  identity-only orders ≤4 (commensurable). No motif miner.

Pass-level decision remains **HOLD** unless F1–F3 fire.

## Relation to the crude desk

This is a sidecar lab, same shelf as AETL-E0. It does **not** amend BR-0001,
does not construct `I_t`, does not open Wave 1, does not change
`2011_nc_first_print_or_stop`.
