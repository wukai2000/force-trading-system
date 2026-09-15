# Wave 0 reckoning — 2026-09-15

Hostile read of a review that treated CER-0001 Wave 0 as
“the discovery architecture becoming testable.” Capital `$0`.
Architecture unchanged. Wave 1 not opened. Gate 1 still the object.

## What the review got right

1. **N1 > G1.** Refusing extra grammar is the load-bearing property.
   20/20 `MARKOV1_ONLY` on SYN-N1 is the best number in the file.
2. **A1 found a real hole.** M2 can beat a broken M1 while both lose to M0.
   Tightening the gate to “M2 must beat M1 *and* M0” was the correct
   class-level fix. Governor laws were not moved. Good.
3. **A1-v1 is development, not certification.** The M0 conjunct was added
   after seeing the first A1 run. Record it that way. Do not cite 20/20
   `REFUTED` as an independent protected-eval result.
4. **Do not start HOU-1 motif search.** Passing Wave 0 does not open Wave 1.
5. **Do not add an architecture layer.** Failure should dictate the next
   primitive, and no failure that requires a new primitive has shown up.
6. **The refusal habit is real.** Electricity, freight, NBI, BR-0001,
   SYN-N1, SYN-A1 after the gate — the system is not optimized to “find
   something.” Keep that.

## What the review overclaimed

1. **Wave 0 did not test adaptive discovery.**
   `aetl/wave0.py` sets `adaptive_iterations: 0`,
   `representations_searched: 1`, `models_searched: [M0, M1, M2]`.
   Mining is locked. PrefixSpan did not run. AETL’s Explorer/Prosecutor
   loop did not run. Nested holdout NLL ran. That is AETL-E0’s cousin,
   not a new laboratory for “animal language.”
2. **SYN-G1 did not recover a grammar.**
   The plant is an intermittent `ABC` trigram. “Recovery” means order-2
   Markov beats M0 and M1 by 6 nats on a 35% holdout. No motif is named.
   No alphabet is discovered. `STATISTICALLY_SUPPORTED` here is extra
   nested-Markov lift, not a Force, not H1, not H2.
3. **15/20 is the pass floor, not encouragement.**
   `pass_G1_recover` is `>= 15`. Same generator as AETL-E0 P2 (17/20 on
   other seeds). Seed-dependent. Do not retune 6 nats to chase 20/20.
4. **The seven-slot portfolio is a register, not an instrument.**
   HOU-1 / COM-1 / ENE-1 / CTL-1 have no Test-0 memo, no lineage, no
   vintage. Names with roles are not experiments.
5. **CER is not the conceptual center.**
   Desk `next_object` is `2011_nc_first_print_or_stop`.
   2014–2016 WPSR cells are sealed. Cells are not `I_t`.
   `e1i_vintages.ok` is refused until the 2011 NC grid exists or the
   program stops. BR-0001 stays `REFUSED_PENDING_PROVENANCE`. TSG is
   `PREMATURE`. force_engine is a downstream kill-switch — and CER is
   not a license to skip the missing negative-control tape.
6. **“Recurring temporal structure → Force” is H1 smuggled as the goal.**
   Frozen ontology is a competing adjustment process inside an identity,
   Path C = `{A,B,U}`. H1 can wait. H2 is closed. Grammar identity is
   not the biggest remaining problem. Missing `I_t` is.

## What the 5/20 G1 misses actually are

Recomputed on the frozen seeds (`n=900`, seed `100+w`). All five are
`MARKOV1_ONLY`. None is the A1 trap (M2 beats M1, loses to M0).

| world | M2−M1 | M2−M0 | M1−M0 | reading |
|---:|---:|---:|---:|---|
| 1 | +5.0 | −59.9 | −64.9 | M1 ate the plant; M2 no lift |
| 14 | +1.3 | −64.7 | −66.1 | same |
| 17 | +4.8 | −64.0 | −68.7 | same |
| 16 | +125.9 | +53.0 | −72.9 | M2 overfit; worse than M0 |
| 19 | +62.7 | +0.2 | −62.5 | M2 overfit |

`ABC` is also a first-order cycle (`A→B`, `B→C`). M1 is supposed to
capture a lot of it. When the holdout realization is thin, M2’s extra
parameters lose. Finite sample + representation overlap. Not search
failure: there was no search.

Do not “finish Wave 0” by adding models until this is 20/20. That would
be chasing. The 5 misses are the calibration.

## A1-v1 vs A1-v2

On the current generator (planted prefix, noise suffix), **13/20** worlds
would have been `STATISTICALLY_SUPPORTED` under the old E0 gate
(M2 vs M1 only). All 13 lose to M0, often by 100+ nats. That is the
hole. After the M0 conjunct: 20/20 `REFUTED`.

Label: **A1-v1 = contaminated development. A1-v2 = current spec, not a
replication.** Do not rerun A1-v1 as evidence.

## Where we are (layers, no promotion)

| Layer | Status |
|---|---|
| force_engine / F1–F3 | Built. Negative controls. No working Force |
| FS-0001.v1 | Frozen. T5 `NO_RESULT` |
| Measurement census | Closed. n_seeds=0 |
| MTS-0001 / BR-0001 | Spec frozen. Gate 1 `UNRESOLVED`. Score refused |
| WPSR 2014–2016 | Cell tape sealed. 135 issues. 27 primary cutoffs bound. Cells ≠ `I_t` |
| E1.I | One bind: 2014-07-02 `I_t=U`, unscored |
| WPSR 2011 NC | Unsealed. EIA HTML archive starts 2011-08-03. Blocks `e1i_vintages.ok` |
| AETL-E0 | Lab only. Nested integrity |
| CER Wave 0 | Nested NLL on synthetics. Pass as lab, not as architecture proof |
| TSG | `PREMATURE`. Mining locked |
| ETL-0001 | Leaky FRED. `NO_HIGHER_ORDER_STRUCTURE` |
| Wave 1 historical | `NOT_OPENED` |
| Finance | Closed. Capital `$0` |

## Next (ordered)

1. **Authorized:** 2011 NC first-print **or stop**. Do not score BR-0001.
   Do not write `e1i_vintages.ok` with a missing NC grid.
2. **Optional lab, does not displace (1):** leave the G1 miss table in
   this file. Do not retune 6 nats. Do not add M3.
3. **Refused:** HOU-1 Test-0 memo, Wave 1, motif search, new episode,
   README rewrite that puts CER at the center, alphabet discovery,
   grammar-equivalence machinery, Force language, tickers.

Sealing 2014–2016 cells was the last authorized crude act on the primary
window. Opening housing because synthetics looked healthy is a cousin hunt.
A missing 2011 archive is a stop, not a prompt to switch domains.
