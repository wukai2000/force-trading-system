# WPSR issue 2014-07-02 — first-print extract

Not a tape. Not a score. One Wednesday.

| Field | Value |
|---|---|
| Release date | 2014-07-02 (Wednesday) |
| Week ending | 2014-06-27 (Friday) |
| Scheduled stamp | ~10:30 ET tables / ~13:00 ET full PDF |
| Source page | https://www.eia.gov/petroleum/supply/weekly/archive/2014/2014_07_02/wpsr_2014_07_02.php |
| Cutoff this issue serves | 2014-07-02 |

## Cells read from `table1.csv` of that issue

| Leg | Issue label | Printed value | Unit |
|---|---|---|---|
| production | Crude Oil Supply (1) Domestic Production | 8442 | thousand bbl/d |
| stocks ex-SPR | Commercial (Excluding SPR) | 384.935 | million bbl |
| product supplied | Products Supplied (26) Total | 19433 | thousand bbl/d |

Prior issue 2014-06-25 `table1.csv` (warmup, not a cutoff by itself):
production 8446 kbd; stocks 388.090 mb; product supplied 18807 kbd.

Four-week Δ is **not** computed here. Needs two more warmup issues.

## Hashes (SHA-256)

```
24ec54a4af651173a9c82d200d6060cdee8f1dd9b4c23d7f930422b0d2c855be  table1.csv
7bd5d3f3b51af80ae24ec9483f150d1beea3fb284c8fd138653680e66520c17f  table4.csv
cc0282a9b1d86097f0b9b555661b3e23c696b6438a1f428990bd3d3c303fab90  table9.csv
7ae92cad942a0bc65d60a1d663d1ee3e492f8ab63976e4f89eaecb7891ea0b72  table1.pdf (not stored)
0ef9e8a3f54086bb9bb61c7a07988225e96d0dd1ba3775af5637c2c2b8490f14  highlights.pdf (not stored)
92b3846d8acbc39a73701f3d3b0c22340ad45365453400d14460c381f59a031f  ../2014-06-25/table1.csv
```

Current EIA PET history pages were not used.

## What this does not do

Does not write `e1i_vintages.ok`.
Does not label A/B/U.
Does not open Gate 2 or TSG fitting.
