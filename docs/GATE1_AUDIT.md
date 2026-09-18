# Gate 1 audit consolidation — 2026-09-14

Three independent Gate 1 writeups. All say UNRESOLVED and
`BR-0001 = REFUSED_PENDING_PROVENANCE`. They are not equal.

Capital $0. No reconstruction. No FS-0001.v1 edit. No new episode.

## Binding spec (repo, not the briefs)

`{A,B,U}` are **states**, not series. FS-0001.v1 is a different frozen Force
hypothesis (demand after cost collapse) and is not the Gate 1 object.

| Item | Frozen value |
|---|---|
| Object | BR-0001 / MTS-0001 / EP-CRUDE-2014 |
| A | demand destruction: production ↓ and product supplied ↓ |
| B | lagged supply: production ↑ and product supplied ↓ |
| U | otherwise, including observational equivalence |
| Physical legs | weekly US crude production, commercial crude stocks, total product supplied |
| Candidate EIA ids | WCRFPUS2; commercial / non-SPR stocks (do not swap SPR-inclusive); WRPUPUS2 |
| WPSR | EIA Weekly Petroleum Status Report, Wednesday ~10:30 ET |
| WPSR is not | BLS PPI / WPS commodity codes |
| Primary window | cutoffs 2014-07-02 … 2016-06-29 (27 four-week decisions in the smoke tape) |
| NC window | cutoffs 2011-01-05 … 2012-06-27 |
| Rule window | 4 weeks ending the Friday before each Wednesday cutoff |
| Horizon | 8 weeks on `x` = sign of production_kbd |
| First-print | the value in that Wednesday's issued WPSR file, not current EIA history, not ALFRED ingest |

ALFRED vintage date is **not** first-print unless independently equal to that issue file.

## How the three memos differ

| | Memo 1 (PPI / FS-0001 hunt) | Memo 2 (spec recovered) | Memo 3 (substituted tape) |
|---|---|---|---|
| Found the spec? | No. Looked for FS-0001.v1 as the crude object | Yes | No; rewrote legs |
| `{A,B,U}` | Ambiguous: series vs states | States | Treated as three series |
| WPSR | Flagged as possible BLS WPS | EIA weekly petroleum | EIA weekly + Fed G.17 |
| Legs | unidentified | production, stocks, product supplied | WCESTUS1, **INDPRO**, WPULEUS3 |
| Cutoffs | years only | locked windows | two invented dates (2011-10-07, 2014-10-10 17:00) |
| Frequency | unknown | weekly | weekly + monthly |
| Useful residue | Correct refusal to invent | Correct missing object: issue files | Contamination |

**Keep Memo 2.** It is the only audit that restated the frozen contract without substitution.

**Keep Memo 1's discipline, drop its ontology.** Refusing to guess series was right. Searching FS-0001.v1 and BLS PPI was a workspace miss, not a spec hole. The spec is in `force_ideas/inventory/mts_0001.yaml` and `br_0001.yaml`.

**Kill Memo 3's tape.** INDPRO is a new observable. Utilization is a new observable. Single October cutoffs are a new experiment. Claiming INDPRO "VERIFIED_FIRST_PRINT" does not license the EIA legs. This is the substitution ban.

## Shared correct findings

1. Current EIA historical / API series are as-revised (PSM benchmark). Not `F_t`.
2. "WPSR generally not revised" is not proof that a 2011 or 2014 cell is the first public print.
3. Archive architecture exists: [WPSR Archives](https://www.eia.gov/petroleum/supply/weekly/archive/) lists 2011 and 2014 release dates. Example issue path: `/petroleum/supply/weekly/archive/2012/2012_03_21/pdf/wpsrall.pdf`.
4. Observation date ≠ release date ≠ vintage date ≠ cutoff.
5. Gate 1 is not an economic FAIL. It is a missing tape.

## What UNRESOLVED means

Not: the petroleum identity cannot be reconstructed.
Not: Path C is dead.
Not: start MTS-0002.

Means: no hashed Wednesday issue file has been bound to the three locked values at any frozen cutoff.

Until that binding exists, BR-0001 stays `REFUSED`. Do not write `UNIDENTIFIABLE` or `NO_RESULT` of the reconstruction. Those require Gate 2.

## What it takes to resolve (Gate 1 PASS)

A PASS is only this sentence becoming true:

> For every decision cutoff in the frozen 2011 and 2014 grids, the three
> first-print values used to code `{A,B,U}` were read from a preserved
> WPSR issue whose release timestamp is ≤ that cutoff, and the 8-week
> production outcome for `x` was read from later issues only after the
> state was sealed.

Operational checklist (order matters):

1. **Do not touch FS-0001.v1.** Different object.
2. **Do not change A, B, U, x, windows, or series.** Memo 3 is closed.
3. **List every required Wednesday**, not two sample dates.
   - Warmup: four WPSR issues before the first cutoff in each window (needed to form the 4-week Δ).
   - Live: every cutoff already in `data/lab/crude/replay_notes.jsonl` (primary 27; NC to be listed the same way).
   - Outcome: eight subsequent production prints after each cutoff, stored separately, not used to build `I_t`.
4. **Retrieve the issue file** from the EIA archive (PDF/CSV/XLS of that release date). Wayback is allowed if the EIA path 404s, if the capture date is ≤ a few days after release and the file is the WPSR issue, not a later page.
5. **Extract three numbers** from that issue: field production, commercial crude stocks excluding SPR, total product supplied. Record table/cell. Do not pull the live PET series page.
6. **Hash and store** `data/lab/crude/wpsr/<release_date>/` plus a row in `data/lab/crude/gate1_ledger.jsonl`.
7. **Boundary test per cutoff:** max(release timestamps of the four warmup issues) ≤ cutoff 10:30 ET Wednesday. Holiday slips stay dated as published, not "usually Wednesday."
8. **Joint assembly:** all three legs present in the same issue (or the same release bundle). One missing leg → that cutoff is `INCOMPLETE`, not filled from today's API.
9. **ALFRED is optional.** If an ALFRED vintage exists for these exact EIA series, it may be cited only after a cell-by-cell match to the issue file. A mismatch → ALFRED is not first-print. Many FRED onsets are 2015 ingest; that cannot backfill 2011.
10. **Initialization ambiguity.** Use the same four-week Δ already used in the as-revised smoke (`d_prod`, `d_demand` over the locked cutoff). Do not pick a prettier warmup.
11. Write `data/lab/crude/e1i_vintages.ok` **only** when every live cutoff row is `FIRST_PRINT_PROVEN` or an explicit `MISSING_ISSUE` (which blocks PASS).

PASS of Gate 1 still does not open Gate 2 scoring automatically. It only makes scoring *eligible*. Harness stays refused until that file exists.

## What would make Gate 1 FAIL (not UNRESOLVED)

Investigate the archive and show that the required issue files do not exist, or that the three legs cannot be read from those files for a material fraction of frozen cutoffs, with no protocol-legal substitute. Then the honest label is Gate 1 `FAIL` / reconstruction `NO_RESULT` because `F_t` cannot be built. That investigation has not been done. Two sample October dates do not count.

## Move-forward order

```
now     keep REFUSED_PENDING_PROVENANCE
next    one-issue proof: 2014-07-02 WPSR file → three cells → hash
then    finish the 2014 grid, then the 2011 grid
then    e1i_vintages.ok
then    Gate 2 eligibility (still not a Force)
never   INDPRO, utilization-as-U, PPI WPS, current PET history as F_t
```

The smallest next act is a single Wednesday, not a dashboard.

## Addendum 2026-09-15 — EP-NC-2011 is not North Carolina

Three search notes were compared (`docs/MEMO_2011_NC_CONSOLIDATION.md`).
Two of them hunted a weekly North Carolina WPSR supply row. That row does
not exist. It was never the frozen object.

`NC` = `EP-NC-2011` = US crude identity, window `2011-01-05 … 2012-06-27`.
Same three legs. Official HTML archive still starts **2011-08-03**.
August 2011 WPSR gasoline-export methodology change is a material vintage
attack on current PET as 2011 `F_t`.

This addendum does **not** flip Gate 1 to FAIL. FAIL still requires the
required US issue files to be unrecoverable, including Wayback. That path
was not exhausted. Missing file → `INCOMPLETE`, not `U`.

`e1i_vintages.ok` remains unwritten. Next object (then):
`2011_ep_nc_us_wpsr_or_fail`.


## Addendum 2026-09-17 — bounded Wayback existence (Jan–Jul 2011)

Authorized: existence of US WPSR issue files for the 30 Wednesdays
`2011-01-05 … 2011-07-27`. Same three Table-1 legs. Not `I_t`. Not a
score. Not North Carolina.

CDX search stayed **503**. Year calendar of the named rolling-current
URLs was enumerated. Live dated HTML sampled 404 except unlisted
**2011-07-27**. Near-release Wayback hits include 2011-01-19 `wpsrall`,
2011-05-11 `table1.pdf`, 2011-05-18 `table1.csv` (three legs in-repo).
June calendar 301s followed to **2011-08-13** — closest-snapshot is not
a week. Receipt: `docs/EP_NC_2011_WAYBACK.md`.

This addendum does **not** flip Gate 1 to FAIL or PASS.
`e1i_vintages.ok` remains unwritten. Next object (then):
`2011_ep_nc_fill_remaining_or_fail`.


## Addendum 2026-09-18 — try reach 2011 first-print

Listed EIA dated archive **2011-08-03 … 2012-06-27** pulled 48/48
`table1.csv` with Last-Modified on the release day. Same method as the
2014–2016 cell tape. Jan–Jul 2011 still a hole: 4 three-leg extracts
(3 Wayback near-release + 1 live unlisted). CDX for `ir.eia.gov`
`table1.csv` Jan–Jul is one capture (2011-05-20). Closest-snapshot
redirects refused.

NC cutoffs every 4 weeks: **12/20** have a listed-archive cell. **8/20**
incomplete. Gate 1 stays **UNRESOLVED**. `e1i_vintages.ok` unwritten.
`I_t` not a series. Next: `2011_jan_jul_hole_or_fail`.


## Addendum 2026-09-18 — eight incomplete NC cutoffs

Authorized bound: those 8 cutoffs only. Healthy CDX + old
`eia.doe.gov` + GovInfo if the file is the issue.

Recovered **3/8** as Table 9 of the same Wednesday issue (not Table 1
CSV): 2011-03-30, 2011-04-27 (xls current-week row only), 2011-07-20.
Orig Last-Modified on the release Wednesday. `id_` only.

Still **INCOMPLETE**: 2011-01-05, 02-02, 03-02, 05-25, 06-22.
GovInfo is not a WPSR issue file. `psw09.xls` history is not first-print
for earlier cutoffs. Dated `archive/2011/` Wayback starts at 2011-08-03.

NC cutoffs **15/20** have an issue. Gate 1 stays **UNRESOLVED**.
`e1i_vintages.ok` unwritten. Next: `2011_five_cutoffs_or_fail`.


## Addendum 2026-09-18 — five remaining cutoffs exhausted → FAIL

Authorized: those five only (`2011-01-05`, `02-02`, `03-02`, `05-25`,
`06-22`). Live dated archive 404. Wayback `id_` of rolling Table 1
collapses to **2011-08-13**. Jan 5 `tabled1.pdf` orig-lm is **30 Dec
2010** (prior week, Appendix D1). Mar 8 landing orig-lm is **24 Feb**.
HathiTrust WPSR fiche ends 2000. IA collections for 2011 WPSR = 0.
GovInfo is not an issue file. ALFRED without cell match refused.

**Gate 1 FAIL.** Reconstruction `NO_RESULT` because `F_t` cannot be
built for 5/20 frozen NC cutoffs. `e1i_vintages.ok` unwritten. `I_t`
not a series. Do not score BR-0001. Next: `stay_frozen`.

