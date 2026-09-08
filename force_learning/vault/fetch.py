"""Re-fetch vault raw sources. Does not unlock T5. Does not fetch SPPI for use."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import requests

RAW = Path(__file__).resolve().parent / "raw"
UA = {"User-Agent": "force-research-vault/1.0 (historical feasibility; no trading)"}

SOURCES = [
    {
        "name": "oecd_itf_trendsfreight",
        "url": "https://sdmx.oecd.org/public/rest/data/OECD.ITF,DSD_TRENDS@DF_TRENDSFREIGHT,/.A.....?dimensionAtObservation=AllDimensions",
        "headers": {"Accept": "application/vnd.sdmx.data+csv;charset=utf-8;labels=both"},
        "suffix": "csv",
    },
    {
        "name": "eurostat_rail_go_total",
        "url": "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/rail_go_total?format=SDMX-CSV&compressed=false",
        "suffix": "csv",
    },
    {
        "name": "eurostat_road_go_ta_tott",
        "url": "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/road_go_ta_tott?format=SDMX-CSV&compressed=false",
        "suffix": "csv",
    },
    {
        "name": "worldbank_rail_tkm",
        "url": "https://api.worldbank.org/v2/country/all/indicator/IS.RRS.GOOD.MT.K6?format=json&per_page=20000",
        "suffix": "json",
    },
    {
        "name": "iea_eei_landing",
        "url": "https://www.iea.org/data-and-statistics/data-product/energy-end-uses-and-efficiency-indicators",
        "suffix": "html",
        "ok_if": {200, 403},
    },
]


def fetch_all() -> List[Dict[str, Any]]:
    RAW.mkdir(parents=True, exist_ok=True)
    out = []
    for src in SOURCES:
        rec: Dict[str, Any] = {"name": src["name"], "url": src["url"]}
        try:
            h = dict(UA)
            h.update(src.get("headers") or {})
            r = requests.get(src["url"], headers=h, timeout=90, allow_redirects=True)
            rec["status_code"] = r.status_code
            rec["n_bytes"] = len(r.content)
            allowed = src.get("ok_if") or {200}
            rec["ok"] = r.status_code in allowed
            if r.status_code == 200 and len(r.content) > 200 and src["suffix"] in {"csv", "json"}:
                (RAW / f"{src['name']}.{src['suffix']}").write_bytes(r.content)
        except Exception as e:
            rec["ok"] = False
            rec["error"] = f"{type(e).__name__}: {e}"
        out.append(rec)
    (RAW / "probes.json").write_text(json.dumps(out, indent=2))
    return out
