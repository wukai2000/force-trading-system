# 2011 NC search — consolidation 2026-09-15

Three notes. One frozen object. Capital `$0`. HOU-1 closed. 6 nats not moved.

**`NC` in this repo is `EP-NC-2011`**, the negative-control window
`2011-01-05 … 2012-06-27` on the **same US crude identity** as EP-CRUDE-2014.
It is not the state of North Carolina.

## What each note actually is

| Source | Object it searched | Verdict it wanted | Status here |
|---|---|---|---|
| Memo A (STOP, D1/PADD 1C) | North Carolina weekly WPSR supply grid | STOP, `I_T_CONSTRUCTIBLE` refused | **Wrong object.** Keep the refusal discipline. Drop the geography. |
| Memo B (PROVENANCE_INSUFFICIENT) | US WPSR production / stocks / product supplied, 2011 window | Provenance stop this pass; not NO_RESULT | **Keep.** Only note that restated the frozen contract. |
| Memo C (STOP, disaggregate 1C) | North Carolina state-level weekly balance sheet | STOP; `I_t=U` for all 2011 | **Wrong object.** `I_t=U` from an empty wrong `F_t` is not a legal U. |

Same failure mode as the 2026-09-14 Gate 1 briefs: Memo 1 hunted FS-0001 / PPI; Memo 3 substituted INDPRO. Searching a name collision is not investigating the archive.

## Keep (law)

1. **EP-NC-2011 = US crude identity, 2011–12 window.** Legs remain weekly US field production, commercial crude stocks excluding SPR, total product supplied. Same `{A,B,U}` rule. Same 4-week cutoff, 8-week horizon. Do not retune.
2. **No geography substitution.** PADD 1C is not North Carolina *and* is not a license to change the frozen US legs. Appendix D1 residential heating-oil prices are a different measurement, season, and family.
3. **No source-family substitution.** TWIP, GDFU, monthly PSM / `pet_stoc_st`, SEDS, ALFRED-without-cell-match, live PET/dnav: refused as `F_t`.
4. **No splice, imputation, or “year ago” columns as first-print.** A later issue restating last week is not the prior Wednesday’s first print.
5. **Missing issue → `INCOMPLETE`, not `U`.** `U` is observational equivalence of A vs B given the three legs. An absent file is not a state assignment.
6. **August 2011 gasoline-export methodology change is material.** EIA (Today in Energy, 2012-03-21): WPSR switched weekly gasoline-export estimation in August 2011. Old model January 2011 exports ~191 kb/d vs Census/PSM 414 kb/d (gap 223 kb/d). Understated exports **overstate** product supplied by about that amount. Current PET history cannot be treated as 2011 `F_t`. This is NC-6 made concrete.
7. **Official HTML archive for 2011 starts 2011-08-03** (data ending 2011-07-29). January–July 2011 issues are absent from that index. Already recorded in `docs/GATE1_TAPE_2014_2016.md`. Confirmed again this pass.
8. **“Generally not revised” ≠ first-print.** EIA FAQ language does not rescue a methodology break or a missing issue file.

## Dismiss

| Item | Why |
|---|---|
| North Carolina as the Gate 1 object | Name collision with `EP-NC-2011`. WPSR never published a weekly NC-state supply row. That is not the frozen hole. |
| Appendix D1 NC heating-oil prices as E1.I | Price, winter-only, later panel. Measurement-boundary choice, not a frozen extraction. |
| PADD 1C for “NC” | Silent geography change. Forbidden even if someone wanted the state. |
| Monthly NC state stocks | Frequency + publication family. |
| `I_t = U` for every 2011 cutoff because the state cell is empty | Wrong `F_t`. Empty file is `INCOMPLETE`. |
| Gate 1 **FAIL** from this pass | FAIL requires showing the **required US WPSR issue files** do not exist for a material fraction, with no protocol-legal substitute. Wayback is still legal (`docs/GATE1_AUDIT.md`). These notes did not exhaust that path on the correct object. |
| Declaring `I_T_CONSTRUCTIBLE` or writing `e1i_vintages.ok` | Not earned. 2011 US first-print grid still missing. |
| Scoring BR-0001, opening Wave 1 / HOU-1, retuning, new episode | Unchanged refusals. |
| Filling Jan–Jul 2011 from live PET or later WPSR restatements | Revision leak. The August 2011 export-method change is why. |

## What this pass actually established

| Claim | Result |
|---|---|
| Official 2011 HTML/CSV WPSR index | Starts **2011-08-03**. Jan–Jul 2011 not listed. |
| US Table 1 cells in those Aug–Dec 2011 issues | Structurally the same object as the sealed 2014–2016 tape (production, stocks, product supplied). Not extracted this pass. |
| North Carolina weekly supply cell | Does not exist. Dismissed as the search target. |
| Product-supplied vintage identity for early 2011 | Attacked, not rescued. Method change in August 2011 is EIA-documented. |
| Complete 2011-01-05 … 2012-06-27 first-print tape | **Not constructed.** |
| One hashed 2011 US issue file in-repo | **None.** (2014-07-02 remains the only bound Wednesday.) |

Gate 1 stays **UNRESOLVED**. `e1i_vintages.ok` is not written. BR-0001 stays `REFUSED_PENDING_PROVENANCE`. Cells are not `I_t`. `I_t` is not a series.

## Hostile question

**Attack:** “The 2011-12-29 WPSR Appendix D1 names North Carolina. That is the 2011 NC first-print.”

**Why that dies:** D1 is not the E1.I cell. `NC` is not a state. A December panel is not 22 first-prints. Jan–Jul 2011 is missing even as a sideline.

**Attack:** “Jan–Jul 2011 is missing from the official HTML index, therefore Gate 1 FAIL.”

**Why that is not yet FAIL:** the frozen FAIL sentence requires the *required US issue files* to be unrecoverable, including Wayback when the EIA path 404s. That search was not completed on EP-NC-2011. HTML-index gap is a PASS blocker. It is not, by itself, a FAIL.

**Attack:** “Then `I_t` is constructible from Aug 2011–Jun 2012 HTML plus current PET for the first half.”

**Why that dies:** splice. The methodology change sits on the splice. Current PET is as-revised. Partial window is not the frozen NC grid.

## Next object

`2011_ep_nc_us_wpsr_or_fail`

If a later session happens: one US WPSR Wednesday inside the frozen control window, same three Table-1 cells as 2014-07-02, hash it. Start with an issue that is **on** the official HTML index (`2011-08-03` or later) so the method is the 2014 method, not a Wayback adventure. Then decide whether Jan–Jul 2011 Wayback is authorized.

Silent default = later. Do not score. Do not open Wave 1. Do not hunt North Carolina.
