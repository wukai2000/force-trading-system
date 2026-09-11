"""Landing-page existence probes for the six physical architectures.

Does not pull vintage catalogs, extract panels, fit lags, or pick famous cases.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests

RAW = Path(__file__).resolve().parent / "raw"
UA = {"User-Agent": "force-research-vault/1.0 (architecture probe; no trading)"}

# Six from the forensic ranking. Not a QUALIFIES quota.
PROBES: List[Dict[str, Any]] = [
    {
        "id": "OA-VOLCANO-ERUPTION",
        "role": "precursor_live_api",
        "url": "https://volcanoes.usgs.gov/vsc/api/volcanoApi/volcanoesUS",
        "note": "live US volcano list; not a frozen pre-eruption catalog",
    },
    {
        "id": "OA-VOLCANO-ERUPTION",
        "role": "transition_current",
        "url": "https://volcanoes.usgs.gov/hans-public/api/volcano/getUSVolcanoes",
        "note": "HANS current volcano records; not GVP chronology vintage",
    },
    {
        "id": "OA-FRA-ATIP",
        "role": "transition_form54",
        "url": "https://data.transportation.gov/resource/85tf-25kj.json?$limit=1",
        "note": "public Form 6180.54 accident extract exists",
    },
    {
        "id": "OA-FRA-ATIP",
        "role": "transition_landing",
        "url": "https://safetydata.fra.dot.gov/",
        "note": "FRA safety data landing",
    },
    {
        "id": "OA-FRA-ATIP",
        "role": "precursor_atip_program",
        "url": "https://railroads.dot.gov/railroad-safety/divisions/track-and-structures/automated-track-inspection-program-atip",
        "ok_if": {200, 404},
        "note": "ATIP program page; raw geometry-car archive not claimed",
    },
    {
        "id": "OA-AIRCRAFT-SDR",
        "role": "precursor_sdr_landing",
        "url": "https://www.faa.gov/av-info/download_SDR",
        "note": "annual SDR CSV landing exists; not a frozen inspection logbook",
    },
    {
        "id": "OA-AIRCRAFT-SDR",
        "role": "transition_ntsb",
        "url": "https://www.ntsb.gov/Pages/CAROL.aspx",
        "note": "NTSB CAROL aviation investigations 1962–present",
    },
    {
        "id": "OA-LANDSLIDE-GEODETIC",
        "role": "inventory_landing",
        "url": "https://www.usgs.gov/programs/landslide-hazards",
        "note": "USGS landslide hazards program; not a frozen InSAR vintage",
    },
    {
        "id": "OA-LANDSLIDE-GEODETIC",
        "role": "gps_archive",
        "url": "https://www.unavco.org/data/gps-gnss/gps-gnss.html",
        "ok_if": {200, 301, 302, 403, 404},
        "note": "EarthScope/UNAVCO GPS access; may redirect",
    },
    {
        "id": "OA-DAM-SURVEILLANCE",
        "role": "inventory_nid",
        "url": "https://nid.sec.usace.army.mil/",
        "note": "NID is a dam STOCK inventory, not instrumentation time series",
    },
    {
        "id": "OA-VESSEL-PSIX",
        "role": "inspection_psix",
        "url": "https://cgmix.uscg.mil/psix/",
        "ok_if": {200, 403, 500},
        "note": "USCG PSIX inspection/deficiency portal",
    },
]


def probe_all() -> List[Dict[str, Any]]:
    RAW.mkdir(parents=True, exist_ok=True)
    out: List[Dict[str, Any]] = []
    for src in PROBES:
        rec: Dict[str, Any] = {
            "id": src["id"],
            "role": src["role"],
            "url": src["url"],
            "note": src.get("note"),
        }
        try:
            r = requests.get(src["url"], headers=UA, timeout=45, allow_redirects=True)
            rec["status_code"] = r.status_code
            rec["n_bytes"] = len(r.content)
            rec["final_url"] = str(r.url)
            allowed = src.get("ok_if") or {200}
            rec["reachable"] = r.status_code in allowed
        except Exception as e:
            rec["reachable"] = False
            rec["error"] = f"{type(e).__name__}: {e}"
        out.append(rec)
    payload = {
        "kind": "landing_page_existence",
        "not": ["vintage_catalog_pull", "famous_event_lineage", "lag_test", "seed"],
        "n_seeds": 0,
        "probed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rows": out,
    }
    (RAW / "physical_survey_probes.json").write_text(json.dumps(payload, indent=2))
    return out
