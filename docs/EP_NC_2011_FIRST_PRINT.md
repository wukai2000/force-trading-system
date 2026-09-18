# EP-NC-2011 — try reach first-print 2026-09-18

Authorized: fill remaining US WPSR issue files for `2011-01-05 … 2012-06-27`.
Not I_t. Not a score. Not North Carolina. Not TWIP. Capital $0.

Prior existence: `docs/EP_NC_2011_WAYBACK.md`.
Cells: `data/lab/crude/wpsr/AUG2011_JUN2012_CELLS.json`,
`data/lab/crude/wpsr/JAN_JUL_2011_CELLS.json`.

## What reached

| Slice | Issues | Vintage | Three legs |
|---|---|---|---|
| 2011-08-03 … 2012-06-27 live dated archive | **48/48** | CSV Last-Modified = release day (Wed or Thu slip) | yes |
| Jan–Jul 2011 hole | 4 of 30 with three legs | mixed | 3 Wayback near-release + 1 live unlisted |

Same method as the 2014–2016 cell tape for the listed slice. Cells ≠ `I_t`.

Holiday slips (Wednesday requested → Thursday file): 2011-09-08, 2011-10-13,
2011-12-29, 2012-01-05, 2012-01-19, 2012-02-23, 2012-05-31.

## Jan–Jul three-leg extracts

| Release | Week ending | prod kbd | stocks mb | supplied kbd | Class |
|---|---|---|---|---|---|
| 2011-01-19 | 2011-01-14 | 5205 | 335.7 | 19189 | Wayback `wpsrall.pdf` (stocks 1 decimal) |
| 2011-05-11 | 2011-05-06 | 5609 | 370.3 | 18164 | Wayback `table1.pdf` (stocks 1 decimal) |
| 2011-05-18 | 2011-05-13 | 5618 | 370.312 | 18515 | Wayback `table1.csv` |
| 2011-07-27 | 2011-07-22 | 5377 | 354.025 | 18426 | live unlisted; not first-print |

Partial, not three legs: 2011-02-16 `table4.pdf` stocks only; 2011-07-20
`wpsrsummary.pdf` stocks 351.7 only (capture 2011-07-26 01:06 UTC still showed
week ending Jul 15).

## What was tried and refused as a week

CDX for `ir.eia.gov/wpsr/table1.csv` **returned** this pass: one Jan–Jul 200
(`20110520195604`). Extra rolling URLs (`wpsrsummary`, `table9`, landing HTML)
did not yield another Table-1 three-leg file. Requesting `table1.csv` at Jul 12
or Jul 26 timestamps **collapsed to May 20**. Closest-snapshot is not a week.

## NC cutoffs (every 4 weeks from 2011-01-05, n=20)

12/20 have a listed-archive cell (2011-08-17 … 2012-06-20, including Thursday
slips). 8/20 sit in the Jan–Jul hole and are still `INCOMPLETE`.

## Gate

**Still UNRESOLVED.** Not FAIL: the listed half exists; some Jan–Jul files exist.
Not PASS: eight NC cutoffs have no three-leg first-print issue. `e1i_vintages.ok`
stays unwritten. Do not score BR-0001. Do not open Wave 1.

Missing issue remains `INCOMPLETE`, not `U`.

## Next

`2011_jan_jul_hole_or_fail`

Silent default = later.
