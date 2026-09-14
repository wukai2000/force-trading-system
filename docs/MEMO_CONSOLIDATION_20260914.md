# Memo consolidation — 2026-09-14

Three design memos asked what E1.I (if it passed) would buy, whether Path C
survives, what the object is, and what to run next. This note records the
comparison and the choices that were implemented.

E1.I has **not** passed. Vintages are **not** constructed. Treating E1.I as a
plumbing assumption is a design fiction only. It is not a lab result.

## What all three memos share

1. E1.I is infrastructure, not economics.
2. A latent Force / fingerprint is the wrong reconstruction object.
3. `{A,B,U}` plus an explicit unidentifiable outcome is the honest alphabet.
4. Blind sequential reconstruction beats after-the-fact narrative.
5. Negative controls must be able to kill the method.
6. Finance stays out. No IR, no tickers, no P&L as success.
7. `UNIDENTIFIABLE` and `NO_RESULT` are different and both legal.

## Where they disagree

| Topic | Memo 1 (CAP / BR-0001) | Memo 2 (Competing-Process State) | Memo 3 (CSCS / E2.I) |
|---|---|---|---|
| Path C | Narrow hard or kill | Retain, demote to observable state | Keep as propagation constraint |
| Object name | CAP | Competing-Process State | CSCS with pressure vectors |
| State vector | `(C, Λ, π, F)` only | Richer card (timing, confidence, alternative) | Magnitude, velocity, persistence, Ω |
| Next experiment | Same 2011/2014 windows | Same episode, more output fields | **New** 2014 transport/storage episode |
| Success | Separate ledgers; always-U may win | Seven independent gates | 75% accuracy, 30-day lead, Brier < 0.15 |
| Kill condition | Cannot freeze A,B,x without the ending | Object instability / NC match | NC-1 any confident call |

## Choices (implemented)

**Keep Memo 1 as the law.** It is the only memo that does not smuggle a new
episode, a fingerprint catalog, or a numeric hero score. It treats `U` as a
first-class outcome and forbids running if `A,B,x` cannot be frozen without
the ending.

**Keep Memo 2’s three propositions** as the scoring split:

1. observable state reconstructible
2. next increment anticipatable
3. mechanisms discriminable

A legal result is `1 PASS / 2 PASS / 3 UNIDENTIFIABLE`.

**Kill Memo 3’s increments:**

- MTS-0002 / E2.I new episode (pipeline / rail / storage)
- CSCS vector physics (`M`, `V`, `τ`, `Ω`)
- 75% / 30-day / Brier 0.15 targets (illegal success criteria this cycle)
- Path C as a pre-assigned multi-domain chain
- any claim that E1.I already passed

**Narrow Path C** to Memo 1’s sentence:

> At cutoff T, using only information dated ≤ T, assign the episode to
> `{A,B,U}` under a frozen coding rule. `U` includes insufficient information
> **and** observationally equivalent mechanisms.

Fingerprint catalogs, dominance poetry, and propagation orderings are out.

**Ontology.** `Force` as a word may remain in repo names. The reconstructible
object is a **competing adjustment process (CAP)**. `Force := CAP candidate`.
Do not hunt a fingerprint.

**Sequence, not a leap.**

```
Gate 0  freeze A, B, x, rubric, NCs, cutoffs     DONE in br_0001.yaml
Gate 1  E1.I true vintages on the same windows   NOT RUN
Gate 2  BR-0001 sealed sequential scoring        REFUSED until Gate 1
Gate 3  finance role-3 incorporation             locked
```

**A, B, x freeze (why this is not HYPOTHESIS_UNFREEZABLE — yet).**

`A` = demand destruction, `B` = lagged supply, `x` = 8-week sign of
`production_kbd` while product supplied is the conditioning leg. Those names
come from the EIA weekly petroleum *identity*, which existed as a public
accounting object long before 2014. They are already locked in
`force_ideas/inventory/mts_0001.yaml`.

Remaining contamination: the *episode window* 2014–16 was chosen because the
completed story is a glut. That cannot be undone. It is why the 2011 control
stays and why a PASS_NARROW still cannot promote a Force.

If a later edit of `A`, `B`, or `x` uses the 2014 ending, record
`HYPOTHESIS_UNFREEZABLE` and stop. Do not run BR-0001.
