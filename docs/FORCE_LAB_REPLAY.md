# Competing-mechanism replay — EP-CRUDE-2014

First experiment after redesign v2. Not a Force. Not a freeze. Capital $0.

## Claim under test

Competing named mechanisms inside a real accounting identity produce ordered footprints that a cutoff-constrained observer can turn into next-state predictions that beat persistence — including on a negative control — without using returns.

## What ran

US commercial crude identity, weekly EIA as-revised files, 5-day WPSR lag, 4-week cutoffs 2014-07-02 to 2016-06-29. Horizon 8 weeks. Scored series: production, stocks, product supplied.

Rule (preregistered): if production↑ and product supplied↓, label B (lagged supply) and predict production↑, stocks↑. If both ↓, label A. Else unidentified → persistence.

Negative control: 2011-01-05 to 2012-06-27, same schema.

Excluded: prices, tickers, DPR rigs (monthly as-revised leak), Baker Hughes (not fetched), financial sidecar.

## Result

| | persist | rule |
|---|---|---|
| overall | 0.617 | 0.642 |
| production | 0.778 | 0.778 |
| stocks | 0.630 | 0.704 |
| product supplied | 0.444 | 0.444 |
| notes | 27 | 27 |
| labels | — | 13 unidentified, 12 B, 2 A |
| 2011 control | 0.441 | 0.441 |

Edge = 0.025 < 0.05. Entire edge is two extra stock hits. Production is persistence.

**Verdict: `NO_RESULT_MARGIN_TOO_SMALL`**

Vintage quality remains AS_REVISED_PLUS_RELEASE_LAG. Revision leak not killed. identified=false.

## Learn

The architecture (identity + pair + cutoff + next-state + persistence baseline + negative control) is the right object. A hairline edge is not identification.

## Dismiss

Particle filters, trade-gap G(t), fingerprint stories, SEMI/WSTS first, grid 2021–24, AI capex, reopening FS-0001, opening the sidecar.

## Next if reopened

True WPSR/ALFRED vintages for the same identity. Not a new episode. Not Baker Hughes until its release calendar is wired. Not finance.
