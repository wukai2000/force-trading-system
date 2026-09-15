#!/usr/bin/env python3
"""ETL-0001: locked encoding + Markov-1 holdout dNLL. Returns forbidden."""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "lab" / "etl"
LOCAL = Path(__file__).resolve().parent.parent / "data" / "lab" / "etl"
C = 0.75
WIN = 60
PREFIX_END = (2009, 12)
HOLD_END = (2019, 12)
STRESS_END = (2023, 12)


def parse_ym(s: str):
    y, m, *_ = s.split("-")
    return int(y), int(m)


def load_series(path: Path):
    out = []
    with path.open() as f:
        r = csv.DictReader(f)
        cols = r.fieldnames or []
        for row in r:
            raw = (row.get(cols[1]) or "").strip()
            if raw in {"", ".", "NA"}:
                continue
            out.append((parse_ym(row[cols[0]]), float(raw)))
    return sorted(out)


def encode(values):
    xs = [v for _, v in values]
    dates = [d for d, _ in values]
    states = []
    for i, d in enumerate(dates):
        if i < WIN:
            states.append((d, "U"))
            continue
        past = [xs[j] - xs[j - 1] for j in range(i - WIN + 1, i)]
        if len(past) < 2:
            states.append((d, "U"))
            continue
        mu = sum(past) / len(past)
        var = sum((p - mu) ** 2 for p in past) / (len(past) - 1)
        sig = math.sqrt(var) if var > 0 else 0.0
        dx = xs[i] - xs[i - 1]
        if sig <= 0:
            states.append((d, "F"))
            continue
        z = dx / sig
        s = "R" if z > C else ("D" if z < -C else "F")
        states.append((d, s))
    return states


def in_span(d, lo, hi):
    return lo <= d <= hi


def fit_markov(seq):
    trans = defaultdict(Counter)
    marg = Counter(seq)
    for a, b in zip(seq, seq[1:]):
        trans[a][b] += 1
    return trans, marg


def nll_markov(seq, trans, marg):
    nll = 0.0
    tot = sum(marg.values()) or 1
    for i, s in enumerate(seq):
        if i == 0:
            p = marg[s] / tot if marg[s] else 1e-12
        else:
            row = trans[seq[i - 1]]
            den = sum(row.values())
            p = (row[s] + 1e-12) / (den + 1e-12 * len(marg)) if den else 1e-12
        nll -= math.log(max(p, 1e-12))
    return nll


def pair_seq(a, b):
    by = {d: s for d, s in a}
    out = []
    for d, s in b:
        if d in by:
            sa = by[d]
            out.append((d, "U" if sa == "U" or s == "U" else sa + s))
    return out


def synthetic_iid(n=700, seed=1):
    rng = random.Random(seed)
    y, m, x = 1980, 1, 100.0
    dates = []
    for _ in range(n):
        dates.append(((y, m), x))
        x += rng.gauss(0, 1)
        m += 1
        if m == 13:
            m = 1
            y += 1
    return dates


def run_pair(name, sa, sb):
    paired = pair_seq(sa, sb)
    raw_pref = [s for d, s in paired if in_span(d, (1985, 1), PREFIX_END)]
    raw_hold = [s for d, s in paired if in_span(d, (2010, 1), HOLD_END)]
    stress = [s for d, s in paired if in_span(d, (2020, 1), STRESS_END)]
    keep = {k for k, n in Counter(raw_pref).items() if n >= 8 and k != "U"}
    keep = set(sorted(keep, key=lambda k: -Counter(raw_pref)[k])[:20])
    pref = [("RARE" if s != "U" and s not in keep else s) for s in raw_pref]
    hold = [("RARE" if s != "U" and s not in keep else s) for s in raw_hold]
    trans, marg = fit_markov(pref)
    nll_m = nll_markov(hold, trans, marg)
    tot = sum(marg.values()) or 1
    nll_iid = sum(-math.log(max((marg[s] / tot) if marg[s] else 1e-12, 1e-12)) for s in hold)
    t2 = defaultdict(Counter)
    for a, b, c in zip(pref, pref[1:], pref[2:]):
        t2[(a, b)][c] += 1
    nll_2 = 0.0
    for i, s in enumerate(hold):
        if i < 2:
            nll_2 -= math.log(max((marg[s] / tot) if marg[s] else 1e-12, 1e-12))
            continue
        row = t2[(hold[i - 2], hold[i - 1])]
        den = sum(row.values())
        if den == 0:
            row1 = trans[hold[i - 1]]
            den1 = sum(row1.values())
            p = (row1[s] + 1e-12) / (den1 + 1e-12 * len(marg)) if den1 else 1e-12
        else:
            p = (row[s] + 1e-12) / (den + 1e-12 * len(marg))
        nll_2 -= math.log(max(p, 1e-12))
    dnll = nll_2 - nll_m
    return {
        "pair": name,
        "n_prefix": len(pref),
        "n_holdout": len(hold),
        "n_stress": len(stress),
        "occupancy_prefix": dict(Counter(pref)),
        "holdout_nll_markov1": round(nll_m, 3),
        "holdout_nll_iid": round(nll_iid, 3),
        "holdout_nll_order2": round(nll_2, 3),
        "delta_nll_order2_minus_markov1": round(dnll, 3),
        "order2_improves_holdout": dnll < -1e-6,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true")
    args = ap.parse_args()
    if args.synthetic:
        out = run_pair("SYNTH_IID", encode(synthetic_iid(700, 1)), encode(synthetic_iid(700, 2)))
        out["pipeline_broken_if_pass"] = out["order2_improves_holdout"]
        print(json.dumps(out, indent=2))
        return 0 if not out["order2_improves_holdout"] else 2
    print(json.dumps({"id": "ETL-0001", "need_csv": str(DATA), "hint": "drop INDPRO.csv UNRATE.csv CPIAUCSL.csv then rerun"}, indent=2))
    if not (DATA / "INDPRO.csv").exists():
        return 0
    enc = {k: encode(load_series(DATA / f"{k}.csv")) for k in ("INDPRO", "UNRATE", "CPIAUCSL")}
    results = [
        run_pair("INDPRO_UNRATE", enc["INDPRO"], enc["UNRATE"]),
        run_pair("INDPRO_CPI", enc["INDPRO"], enc["CPIAUCSL"]),
        run_pair("UNRATE_CPI", enc["UNRATE"], enc["CPIAUCSL"]),
    ]
    any_pass = any(r["order2_improves_holdout"] for r in results)
    print(json.dumps({
        "id": "ETL-0001",
        "vintage_label": "LEAKY_FRED_AS_REVISED",
        "pairs": results,
        "any_order2_improves_holdout": any_pass,
        "label": "STRUCTURE_CANDIDATE" if any_pass else "NO_HIGHER_ORDER_STRUCTURE",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
