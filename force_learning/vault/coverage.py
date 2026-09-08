"""Coverage / missingness only. No efficiency-shock search. No ΔDemand."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pandas as pd

VAULT = Path(__file__).resolve().parent
RAW = VAULT / "raw"
META = VAULT / "metadata"
OUT = META / "coverage.json"

EU27 = {
    "AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU",
    "GRC", "HUN", "IRL", "ITA", "LVA", "LTU", "LUX", "MLT", "NLD", "POL", "PRT",
    "ROU", "SVK", "SVN", "ESP", "SWE",
}
PHYS = {"ROAD", "RAIL", "IWW", "PIPE", "COASTAL", "TOT_INL"}


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _cover(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {"n_obs": 0, "n_geo": 0, "n_years": 0, "year_min": None, "year_max": None}
    return {
        "n_obs": int(len(df)),
        "n_geo": int(df["geo"].nunique()),
        "n_years": int(df["year"].nunique()),
        "year_min": int(df["year"].min()),
        "year_max": int(df["year"].max()),
        "n_geo_mode_year": int(df.groupby(["geo", "mode", "year"]).ngroups)
        if "mode" in df.columns
        else int(df.groupby(["geo", "year"]).ngroups),
        "estimated": int((df["status"] == "E").sum()) if "status" in df.columns else 0,
        "breaks": int((df["status"] == "B").sum()) if "status" in df.columns else 0,
    }


def oecd_tkm() -> Dict[str, Any]:
    p = RAW / "oecd_itf_trendsfreight.csv"
    if not p.exists():
        return {"wired": False, "reason": "raw file missing; run fetch"}
    df = pd.read_csv(p, low_memory=False)
    df["year"] = pd.to_numeric(df["TIME_PERIOD: Time period"], errors="coerce")
    df["geo"] = df["REF_AREA: Reference area"].astype(str).str.split(":").str[0]
    df["mode"] = df["TRANSPORT_MODE: Transport mode"].astype(str).str.split(":").str[0]
    df["val"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    df["status"] = df["OBS_STATUS: Observation status"].astype(str).str.split(":").str[0]
    sub = df[df["mode"].isin(PHYS) & df["val"].notna() & df["status"].ne("M")]
    w = sub[(sub["year"] >= 2000) & (sub["year"] <= 2024)]
    return {
        "wired": True,
        "unit": "million_tkm",
        "source": "OECD.ITF DSD_TRENDS@DF_TRENDSFREIGHT",
        "currency_present": False,
        "energy_present": False,
        "all_nonmissing": _cover(sub),
        "window_2000_2024": _cover(w),
        "eu_2000_2024": _cover(w[w["geo"].isin(EU27)]),
        "by_mode_2000_2024": {
            m: {
                "n_obs": int((w["mode"] == m).sum()),
                "n_geo": int(w.loc[w["mode"] == m, "geo"].nunique()),
            }
            for m in sorted(w["mode"].unique())
        },
        "sha256": _sha256(p),
        "n_bytes": p.stat().st_size,
    }


def eurostat_rail() -> Dict[str, Any]:
    p = RAW / "eurostat_rail_go_total.csv"
    if not p.exists():
        return {"wired": False}
    df = pd.read_csv(p, low_memory=False)
    df = df[df["unit"].astype(str).eq("MIO_TKM")].copy()
    df["year"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce")
    df["geo"] = df["geo"].astype(str)
    df["val"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    df["mode"] = "RAIL"
    df["status"] = df["OBS_FLAG"].fillna("").astype(str).str.upper().str[:1]
    obs = df[df["val"].notna()]
    w = obs[(obs["year"] >= 2000) & (obs["year"] <= 2024)]
    return {
        "wired": True,
        "unit": "million_tkm",
        "source": "ESTAT:RAIL_GO_TOTAL",
        "window_2000_2024": _cover(w),
        "sha256": _sha256(p),
        "n_bytes": p.stat().st_size,
    }


def worldbank_rail() -> Dict[str, Any]:
    p = RAW / "worldbank_rail_tkm.json"
    if not p.exists():
        return {"wired": False, "role": "cross_check_not_primary"}
    payload = json.loads(p.read_text())
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    vals = [r for r in rows if r.get("value") is not None]
    years = [int(r["date"]) for r in vals]
    return {
        "wired": True,
        "role": "cross_check_not_primary",
        "indicator": "IS.RRS.GOOD.MT.K6",
        "n_obs": len(vals),
        "n_geo": len({r.get("countryiso3code") for r in vals}),
        "year_min": min(years) if years else None,
        "year_max": max(years) if years else None,
        "sha256": _sha256(p),
        "n_bytes": p.stat().st_size,
    }


def build() -> Dict[str, Any]:
    oecd = oecd_tkm()
    report = {
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "force_id": "FS-0001",
        "episode_search": False,
        "t5_ready": False,
        "decision": "NO_RESULT",
        "new_version_required": False,
        "reason": (
            "Aggregate tkm is now coverage-wired from OECD/ITF. IEA energy is 403. "
            "No currency/tkm series in the OECD freight file. Unit cost remains the "
            "blocker. Three-observable contract is not satisfied."
        ),
        "efficiency": {"status": "unwired", "source": "IEA_EEI", "http": 403},
        "unit_cost": {
            "status": "critical_blocker",
            "currency_in_oecd_tkm_file": False,
            "sppi_refused": True,
        },
        "aggregate_use": oecd,
        "eu_geography": {
            "named": "European_Union",
            "oecd_eu_2000_2024": (oecd.get("eu_2000_2024") if oecd.get("wired") else {}),
            "eurostat_rail": eurostat_rail(),
        },
        "cross_check": worldbank_rail(),
        "cannot_promote": True,
        "capital": 0,
    }
    META.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))
    return report
