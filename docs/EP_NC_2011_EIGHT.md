# EP-NC-2011 — bounded retry of 8 incomplete NC cutoffs 2026-09-18

Authorized: those 8 cutoffs only. Healthy CDX + old `eia.doe.gov` paths
+ GovInfo if the file is the issue. Not I_t. Not a score. Not North
Carolina. Not TWIP. Capital $0.

The 8: 2011-01-05, 02-02, 03-02, 03-30, 04-27, 05-25, 06-22, 07-20.

## What this bound found

| Cutoff | Week ending | prod kbd | stocks mb | supplied kbd | File | Class |
|---|---|---|---|---|---|---|
| 2011-03-30 | 2011-03-25 | 5568 | 355.712 | 18605 | Wayback `ir.eia.gov` `table9.csv` (capture 20110401; orig-lm Wed 30 Mar 2011 14:21 GMT) | WAYBACK_NEAR_RELEASE_TABLE9 |
| 2011-04-27 | 2011-04-22 | 5610 | 363.125 | 19588 | Wayback `psw09.xls` **current-week row only** (capture 20110428; orig-lm Wed 27 Apr 2011 13:12 GMT) | WAYBACK_NEAR_RELEASE_TABLE9_XLS_CURRENT_WEEK |
| 2011-07-20 | 2011-07-15 | 5591 | 351.729 | 18853 | Wayback `table9.pdf` + `psw09.xls` current-week (capture 20110725; orig-lm Wed 20 Jul 2011) | WAYBACK_NEAR_RELEASE_TABLE9 |

Table 9 of the same Wednesday issue bundle, not Table 1 CSV. Gate 1
allows the issue (or the same release bundle) if the three US legs are
present. Recorded table/cell. Cells ≠ `I_t`.

Jul 20 PDF printed stocks 351.7 (1 decimal). Machine cell is WCESTUS1
351729 thousand barrels = 351.729 mb from the same-issue xls.

## Exhausted in this bound, still INCOMPLETE

| Cutoff | In-window CDX | Note |
|---|---|---|
| 2011-01-05 | `tabled1.pdf` 200 | Appendix D1. Refused. |
| 2011-02-02 | figures D1–D4 | Not Table 1 / 9. |
| 2011-03-02 | `rdate_wpsr.txt` | Landing widget: “Release date: March 2, 2011”. Not cells. |
| 2011-05-25 | 301s only | Not followed as a week. |
| 2011-06-22 | 301s | Already known to collapse to 2011-08-13. Closest-snapshot refused. |

## What was queried

- CDX **healthy** (canary `ir.eia.gov/wpsr/table1.csv` returned).
- Prefix: `ir.eia.gov/wpsr/`, `eia.doe.gov` and `eia.gov` rolling
  `current/`, landing HTML, FTP (0 rows), dated `archive/2011/`
  (22,199 later captures, first folder **2011-08-03**; the 8 dated
  folders are absent).
- In-window = capture date in `[D−1, D+5]` **and** orig Last-Modified
  on the Wednesday. `id_` only. `available/` refused.
- GovInfo: public search shell empty; `api.govinfo.gov/search` 401;
  POST `/wssearch/search` 400. Web hits are hearings / FR notices, not
  a WPSR issue file.

## Refused

`psw09.xls` **history** is the weekly series as-of that Wednesday.
Only the current-week row is the issue. Earlier rows are not first-print
for the five remaining cutoffs. Do not splice Jan–May from the Apr 27
workbook.

## Gate

**Still UNRESOLVED.** Not FAIL: three of eight now have a near-release
three-leg issue file; listed 2011-08-03…2012-06-27 still 48/48. Not PASS:
five NC cutoffs still `INCOMPLETE`. `e1i_vintages.ok` unwritten. Do not
score BR-0001.

Missing issue remains `INCOMPLETE`, not `U`.

## Next

`2011_five_cutoffs_or_fail`

Silent default = later.
