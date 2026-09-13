"""Competing-mechanism replay. Next-state vs persistence. No returns."""
from __future__ import annotations

import csv
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[2]
INV = ROOT / "force_ideas" / "inventory"
DATA = ROOT / "data" / "lab" / "crude" / "eia_weekly_as_revised.csv"
SPEC = INV / "replay_crude.yaml"
OUT = ROOT / "data" / "lab" / "crude"


class ReplayError(RuntimeError):
    pass


def _d(s: str) -> date:
    return datetime.strptime(s[:10], "%Y-%m-%d").date()


def load_spec() -> Dict[str, Any]:
    return yaml.safe_load(SPEC.read_text()) or {}


def load_panel() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with DATA.open() as f:
        for r in csv.DictReader(f):
            rec: Dict[str, Any] = {"week_ending": _d(r["week_ending"])}
            for k, v in r.items():
                if k == "week_ending" or v in ("", None):
                    continue
                rec[k] = float(v)
            rows.append(rec)
    rows.sort(key=lambda x: x["week_ending"])
    return rows


def _available(week_ending: date, cutoff: date, lag: int) -> bool:
    return week_ending + timedelta(days=lag) <= cutoff


def _idx_on_or_before(rows: List[Dict[str, Any]], cutoff: date, lag: int) -> Optional[int]:
    last = None
    for i, r in enumerate(rows):
        if _available(r["week_ending"], cutoff, lag):
            last = i
        else:
            break
    return last


def _chg(rows: List[Dict[str, Any]], i: int, key: str, weeks: int) -> Optional[float]:
    j = i - weeks
    if j < 0:
        return None
    a, b = rows[i].get(key), rows[j].get(key)
    if a is None or b is None:
        return None
    return a - b


def _sign(x: Optional[float]) -> Optional[int]:
    if x is None:
        return None
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def _label(d_prod: Optional[float], d_dem: Optional[float]) -> str:
    if d_prod is None or d_dem is None:
        return "unidentified"
    if d_prod > 0 and d_dem < 0:
        return "B"  # lagged supply
    if d_prod < 0 and d_dem < 0:
        return "A"  # demand destruction with supply response
    return "unidentified"


def _rule_pred(label: str, persist: Dict[str, Optional[int]]) -> Dict[str, Optional[int]]:
    if label == "B":
        return {"production_kbd": 1, "stocks_kb": 1, "product_supplied_kbd": persist.get("product_supplied_kbd")}
    if label == "A":
        return {"production_kbd": -1, "stocks_kb": persist.get("stocks_kb"), "product_supplied_kbd": -1}
    return persist


def replay_window(
    rows: List[Dict[str, Any]],
    start: date,
    end: date,
    lag: int,
    horizon: int,
    every: int,
) -> List[Dict[str, Any]]:
    notes: List[Dict[str, Any]] = []
    cutoff = start
    while cutoff <= end:
        i = _idx_on_or_before(rows, cutoff, lag)
        if i is None or i + horizon >= len(rows) or i < horizon:
            cutoff += timedelta(weeks=every)
            continue
        keys = ("production_kbd", "stocks_kb", "product_supplied_kbd")
        persist = {k: _sign(_chg(rows, i, k, horizon)) for k in keys}
        actual = {}
        ok = True
        for k in keys:
            now, fut = rows[i].get(k), rows[i + horizon].get(k)
            if now is None or fut is None:
                ok = False
                break
            actual[k] = _sign(fut - now)
        if not ok:
            cutoff += timedelta(weeks=every)
            continue
        d_prod = _chg(rows, i, "production_kbd", horizon)
        d_dem = _chg(rows, i, "product_supplied_kbd", horizon)
        d_stk = _chg(rows, i, "stocks_kb", horizon)
        lab = _label(d_prod, d_dem)
        pred = _rule_pred(lab, persist)
        note = {
            "cutoff": cutoff.isoformat(),
            "last_week_ending": rows[i]["week_ending"].isoformat(),
            "label": lab,
            "d_prod": d_prod,
            "d_demand": d_dem,
            "d_stocks": d_stk,
            "persist": persist,
            "rule": pred,
            "actual": actual,
        }
        notes.append(note)
        cutoff += timedelta(weeks=every)
    return notes


def _hit(pred: Dict[str, Optional[int]], actual: Dict[str, Optional[int]], key: str) -> Optional[int]:
    p, a = pred.get(key), actual.get(key)
    if p is None or a is None or p == 0:
        return None
    return int(p == a)


def score(notes: List[Dict[str, Any]]) -> Dict[str, Any]:
    keys = ("production_kbd", "stocks_kb", "product_supplied_kbd")
    out: Dict[str, Any] = {"n": len(notes)}
    for src in ("persist", "rule"):
        hits = {k: 0 for k in keys}
        n = {k: 0 for k in keys}
        for note in notes:
            for k in keys:
                h = _hit(note[src], note["actual"], k)
                if h is None:
                    continue
                n[k] += 1
                hits[k] += h
        out[src] = {
            k: {"hits": hits[k], "n": n[k], "acc": (hits[k] / n[k] if n[k] else None)}
            for k in keys
        }
        tot_h, tot_n = sum(hits.values()), sum(n.values())
        out[src]["overall"] = {"hits": tot_h, "n": tot_n, "acc": (tot_h / tot_n if tot_n else None)}
    labels = {}
    for note in notes:
        labels[note["label"]] = labels.get(note["label"], 0) + 1
    out["labels"] = labels
    rp = out["rule"]["overall"]["acc"]
    pp = out["persist"]["overall"]["acc"]
    out["beats_persistence"] = bool(rp is not None and pp is not None and rp > pp)
    out["edge"] = (rp - pp) if (rp is not None and pp is not None) else None
    return out



def run() -> Dict[str, Any]:
    spec = load_spec()
    rows = load_panel()
    lag = int(spec["release_lag_days"])
    horizon = int(spec["horizon_weeks"])
    every = int(spec["cutoff_every_weeks"])
    a, b = spec["window"]
    notes = replay_window(rows, _d(a), _d(b), lag, horizon, every)
    primary = score(notes)
    nc = spec["negative_control"]
    nc_notes = replay_window(rows, _d(nc["window"][0]), _d(nc["window"][1]), lag, horizon, every)
    control = score(nc_notes)
    beats = primary["beats_persistence"]
    edge = primary.get("edge")
    min_edge = float(spec.get("min_edge") or 0.05)
    same_on_nc = control["beats_persistence"] and beats
    one_series = False
    if beats:
        accs = [primary["rule"][k]["acc"] for k in spec["scored_series"] if primary["rule"][k]["acc"] is not None]
        if accs and max(accs) - min(accs) > 0.35:
            one_series = True
    if spec["vintage_quality"] != "AS_REVISED_PLUS_RELEASE_LAG":
        verdict = "INVALID_SPEC"
    elif not beats:
        verdict = "NO_RESULT_DOES_NOT_BEAT_PERSISTENCE"
    elif edge is not None and edge < min_edge:
        verdict = "NO_RESULT_MARGIN_TOO_SMALL"
    elif same_on_nc:
        verdict = "NO_RESULT_NEGATIVE_CONTROL_ALSO_EXPLAINED"
    elif one_series:
        verdict = "NO_RESULT_ONE_SERIES"
    else:
        verdict = "BEATS_PERSISTENCE_BUT_REVISION_LEAK"

    result = {
        "id": spec["id"],
        "status": spec["status"],
        "vintage_quality": spec["vintage_quality"],
        "identified": False,
        "n_seeds": 0,
        "capital": 0,
        "financial_sidecar": "sealed",
        "verdict": verdict,
        "primary": primary,
        "negative_control": {"id": nc["id"], **control},
        "n_notes": len(notes),
        "n_nc_notes": len(nc_notes),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "replay_result.json").write_text(json.dumps(result, indent=2))
    (OUT / "replay_notes.jsonl").write_text("\n".join(json.dumps(n, default=str) for n in notes) + "\n")
    return result


def assert_replay() -> Dict[str, Any]:
    spec = load_spec()
    if spec.get("tickers"):
        raise ReplayError("no tickers")
    if spec.get("financial_sidecar") != "sealed":
        raise ReplayError("sidecar sealed")
    if spec.get("identified") is not False:
        raise ReplayError("not identified")
    if spec.get("n_seeds") != 0:
        raise ReplayError("n_seeds 0")
    if spec.get("dpr_rigs") != "excluded_as_revised_monthly_leak":
        raise ReplayError("DPR excluded")
    if spec.get("prices") != "excluded":
        raise ReplayError("prices excluded")
    if not DATA.exists():
        raise ReplayError("fixture missing")
    return spec
