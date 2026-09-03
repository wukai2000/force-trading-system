"""
Four-clock bus + L4 GPR veto (Caldara–Iacoviello).

Clocks may VETO a passing residual. They never promote a failing one.
GPR is veto-only. Synthetic GPR is never written to the production cache.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Optional

import numpy as np
import pandas as pd

from .dates import naive_day_index


LeadingReader = Callable[[], Optional[float]]

ROOT = Path(__file__).resolve().parents[1]
LOCAL_GPR_PATH = ROOT / "data" / "macro" / "gpr_daily.csv"

# Real Iacoviello files (NOT invented domains). Daily recent .xls is the live series.
GPR_DAILY_XLS = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"
GPR_MONTHLY_XLS = "https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls"
GPR_PAGE = "https://www.matteoiacoviello.com/gpr.htm"
GPR_AI_PAGE = "https://www.matteoiacoviello.com/ai_gpr.html"

HIGH_VETO_CLOCKS = {"gpr_z", "gpr"}
HIGH_VETO_Z = 2.0
LOW_VETO_Z = -1.5


@dataclass
class ClockState:
    price_residual: Optional[float] = None
    leading: Dict[str, Optional[float]] = field(default_factory=dict)
    naming: Optional[float] = None
    joint_shift: Optional[float] = None
    veto: bool = False
    veto_reason: str = ""
    gpr_source: str = "unwired"


LEADING_CLOCK_SLOTS = (
    "real_10y_yield",
    "health_expenditure",
    "patent_filings",
    "legislation",
    "credit_spreads",
    "gpr_z",
)


class ClockBus:
    """Collects clock readings. Leading clocks veto; they never promote."""

    def __init__(self):
        self.leading_providers: Dict[str, LeadingReader] = {}

    def register_leading(self, name: str, reader: LeadingReader):
        self.leading_providers[name] = reader

    def read(self, residual_last: Optional[float] = None) -> ClockState:
        leading: Dict[str, Optional[float]] = {}
        for name, reader in self.leading_providers.items():
            try:
                leading[name] = reader()
            except Exception:
                leading[name] = None
        return ClockState(
            price_residual=residual_last,
            leading=leading,
            naming=None,
            joint_shift=None,
        )

    @staticmethod
    def veto_if_leading_contradicts(state: ClockState, residual_ir: float) -> ClockState:
        """
        A *passing* residual can be vetoed if a wired leading clock opposes.
        NaN clocks never veto. Leading clocks cannot rescue FAIL_GATE.
        GPR: z >= +2.0 is a shock veto (positive). Other clocks: val < -1.5.
        """
        if residual_ir < 0.40:
            return state
        for name, val in state.leading.items():
            if val is None or (isinstance(val, float) and pd.isna(val)):
                continue
            if name in HIGH_VETO_CLOCKS and val >= HIGH_VETO_Z:
                state.veto = True
                state.veto_reason = f"leading clock '{name}'={val:.2f} GPR/shock veto"
                break
            if name not in HIGH_VETO_CLOCKS and val < LOW_VETO_Z:
                state.veto = True
                state.veto_reason = f"leading clock '{name}'={val:.2f} opposes residual"
                break
        return state


def _unwired() -> Optional[float]:
    return None


def real_10y_stub() -> Optional[float]:
    """DFII10 opposition from catalog cache; None if missing (no veto)."""
    try:
        from .leading_observables import opposition_reader

        return opposition_reader("dfii10")()
    except Exception:
        return None


def health_expenditure_stub() -> Optional[float]:
    return None


def patent_filings_stub() -> Optional[float]:
    return None


def legislation_stub() -> Optional[float]:
    return None


def credit_spreads_stub() -> Optional[float]:
    """HY OAS opposition (high OAS → negative). None if cache missing."""
    try:
        from .leading_observables import opposition_reader

        return opposition_reader("hy_oas")()
    except Exception:
        return None


def _parse_gpr_xls(path: Path) -> pd.DataFrame:
    import xlrd

    wb = xlrd.open_workbook(str(path))
    sh = wb.sheet_by_index(0)
    headers = [str(sh.cell_value(0, c)).strip() for c in range(sh.ncols)]
    rows = []
    for r in range(1, sh.nrows):
        rows.append([sh.cell_value(r, c) for c in range(sh.ncols)])
    df = pd.DataFrame(rows, columns=headers)
    if "DAY" in df.columns:
        day = df["DAY"].astype(str).str.replace(r"\.0$", "", regex=True)
        idx = naive_day_index(pd.to_datetime(day, format="%Y%m%d", errors="coerce"))
    elif "date" in df.columns:
        idx = naive_day_index(df["date"])
    else:
        raise ValueError("GPR xls missing DAY/date column")
    gpr_col = "GPRD" if "GPRD" in df.columns else next(
        (c for c in df.columns if str(c).upper().startswith("GPR")), df.columns[1]
    )
    gpr = pd.Series(pd.to_numeric(df[gpr_col], errors="coerce").to_numpy(), index=idx, name="gpr_index")
    gpr = gpr[~gpr.index.duplicated(keep="last")].dropna().sort_index()
    out = pd.DataFrame({"gpr_index": gpr})
    if "GPRD_THREAT" in df.columns:
        threat = pd.Series(pd.to_numeric(df["GPRD_THREAT"], errors="coerce").to_numpy(), index=idx)
        out["gpr_threat"] = threat.reindex(out.index)
    out.attrs["source"] = "iacoviello"
    return out


def fetch_real_gpr(cache_path: Optional[Path] = None, timeout: int = 20) -> pd.DataFrame:
    """Download the real Iacoviello daily xls and cache a CSV. No synthetic write."""
    import requests

    cache_path = Path(cache_path) if cache_path is not None else LOCAL_GPR_PATH
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    xls_tmp = cache_path.parent / "data_gpr_daily_recent.xls"
    resp = requests.get(GPR_DAILY_XLS, timeout=timeout)
    resp.raise_for_status()
    xls_tmp.write_bytes(resp.content)
    df = _parse_gpr_xls(xls_tmp)
    df.to_csv(cache_path)
    return df


def load_gpr_cache(cache_path: Optional[Path] = None) -> Optional[pd.DataFrame]:
    cache_path = Path(cache_path) if cache_path is not None else LOCAL_GPR_PATH
    if not cache_path.exists():
        return None
    df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
    df.index = naive_day_index(df.index)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    if "gpr_index" not in df.columns:
        df = df.rename(columns={df.columns[0]: "gpr_index"})
    return df.dropna(subset=["gpr_index"])


class GPRVetoClock:
    """Veto-only. source is iacoviello | cache | unwired | synthetic-test (env only)."""

    def __init__(self, cache_path=None, z_threshold: float = HIGH_VETO_Z, lookback_days: int = 252):
        self.cache_path = Path(cache_path) if cache_path is not None else LOCAL_GPR_PATH
        self.z_threshold = z_threshold
        self.lookback_days = lookback_days
        self.df: Optional[pd.DataFrame] = None
        self.source = "unwired"

    def _synthetic_for_tests(self) -> pd.DataFrame:
        dates = pd.bdate_range("2015-01-01", "2026-08-31")
        rng = np.random.default_rng(42)
        gpr = 100 + rng.exponential(scale=15, size=len(dates))
        return pd.DataFrame({"gpr_index": gpr}, index=dates)

    def fetch_and_cache_gpr_data(self, force_refresh: bool = False) -> pd.DataFrame:
        allow_synth = os.environ.get("FORCE_GPR_SYNTHETIC") in ("1", "true", "TRUE")
        if (not force_refresh) and self.cache_path.exists():
            cached = load_gpr_cache(self.cache_path)
            if cached is not None and len(cached) >= 60:
                self.df = cached
                self.source = "cache"
                return self.df
        try:
            self.df = fetch_real_gpr(self.cache_path)
            self.source = "iacoviello"
            return self.df
        except Exception as exc:
            print(f"[L4-WIRE] real GPR fetch failed ({exc}). source=unwired.")
            if allow_synth:
                print("[L4-WIRE] FORCE_GPR_SYNTHETIC=1 — test series only, not a Caldara fact.")
                self.df = self._synthetic_for_tests()
                self.source = "synthetic-test"
                return self.df
            self.df = None
            self.source = "unwired"
            raise

    def compute_veto_series(self, target_index=None) -> pd.DataFrame:
        if self.df is None:
            cached = load_gpr_cache(self.cache_path)
            if cached is not None:
                self.df = cached
                self.source = "cache"
            else:
                raise FileNotFoundError("GPR cache missing and fetch not run; source=unwired")
        df_calc = self.df.copy()
        rolling_mean = df_calc["gpr_index"].rolling(window=self.lookback_days, min_periods=60).mean()
        rolling_std = df_calc["gpr_index"].rolling(window=self.lookback_days, min_periods=60).std()
        df_calc["gpr_zscore"] = (df_calc["gpr_index"] - rolling_mean) / (rolling_std + 1e-8)
        df_calc["veto_active"] = df_calc["gpr_zscore"] >= self.z_threshold
        df_calc["source"] = self.source
        if target_index is not None:
            tgt = naive_day_index(target_index)
            aligned = df_calc.reindex(tgt, method="ffill")
            aligned["veto_active"] = aligned["veto_active"].fillna(False)
            aligned["gpr_zscore"] = aligned["gpr_zscore"].fillna(0.0)
            return aligned
        return df_calc

    def latest_z(self) -> Optional[float]:
        try:
            series = self.compute_veto_series()
        except FileNotFoundError:
            return None
        z = series["gpr_zscore"].dropna()
        if z.empty:
            return None
        return float(z.iloc[-1])


def gpr_z_reader() -> Optional[float]:
    clock = GPRVetoClock()
    return clock.latest_z()


DEFAULT_LEADING_READERS: Dict[str, LeadingReader] = {
    "real_10y_yield": real_10y_stub,
    "health_expenditure": health_expenditure_stub,
    "patent_filings": patent_filings_stub,
    "legislation": legislation_stub,
    "credit_spreads": credit_spreads_stub,
    "gpr_z": gpr_z_reader,
}


def default_clock_bus() -> ClockBus:
    bus = ClockBus()
    for name, reader in DEFAULT_LEADING_READERS.items():
        bus.register_leading(name, reader)
    return bus


def catalog_clock_bus(macro_dir=None) -> ClockBus:
    """Default slots plus every wired *veto* observable from the catalog."""
    from .leading_observables import load_catalog, register_catalog_on_bus

    bus = default_clock_bus()
    return register_catalog_on_bus(bus, catalog=load_catalog(), macro_dir=macro_dir)
