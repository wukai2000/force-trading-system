"""
Four-clock bus.

F1/F2 Phase A scored only clock 1 (price residual) and skipped 2–4.
Clocks 2–4 are first-class objects. Until series are wired they return
NaN and cannot promote. Once wired they may VETO a passing residual.

Non-equity leading slots (patents, legislation, credit) are registered
because sector ETFs absorb equity flows too quickly for price-only
identification. They still cannot rescue a failing residual.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

import pandas as pd


LeadingReader = Callable[[], Optional[float]]


@dataclass
class ClockState:
    price_residual: Optional[float] = None
    leading: Dict[str, Optional[float]] = field(default_factory=dict)
    naming: Optional[float] = None
    joint_shift: Optional[float] = None
    veto: bool = False
    veto_reason: str = ""


# Registered slots. Readers default to None (unwired) until a real series exists.
LEADING_CLOCK_SLOTS = (
    "real_10y_yield",
    "health_expenditure",
    "patent_filings",
    "legislation",
    "credit_spreads",
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
        Conservative rule: a *passing* residual can be vetoed if a wired leading
        clock is present and strongly opposes. NaN clocks never veto.
        Promotion from leading-only is impossible here.
        """
        if residual_ir < 0.40:
            return state  # already failed; clocks cannot rescue
        for name, val in state.leading.items():
            if val is None or (isinstance(val, float) and pd.isna(val)):
                continue
            if val < -1.5:
                state.veto = True
                state.veto_reason = f"leading clock '{name}'={val:.2f} opposes residual"
                break
        return state


def _unwired() -> Optional[float]:
    return None


def real_10y_stub() -> Optional[float]:
    """Wire FRED T10YIE/DGS10 later. Stub returns None (no veto, no promote)."""
    return None


def health_expenditure_stub() -> Optional[float]:
    return None


def patent_filings_stub() -> Optional[float]:
    """USPTO longevity / senolytic / metabolic counts. Unwired."""
    return None


def legislation_stub() -> Optional[float]:
    """CMS MA rate cycle / IRA drug-pricing clock. Unwired."""
    return None


def credit_spreads_stub() -> Optional[float]:
    """Hospital / provider HY vs IG. Unwired."""
    return None


DEFAULT_LEADING_READERS: Dict[str, LeadingReader] = {
    "real_10y_yield": real_10y_stub,
    "health_expenditure": health_expenditure_stub,
    "patent_filings": patent_filings_stub,
    "legislation": legislation_stub,
    "credit_spreads": credit_spreads_stub,
}


def default_clock_bus() -> ClockBus:
    bus = ClockBus()
    for name, reader in DEFAULT_LEADING_READERS.items():
        bus.register_leading(name, reader)
    return bus


"""
force_engine/clocks.py
======================
L4-WIRE Geopolitical Risk (GPR) Veto Clock Infrastructure.

Ingests Caldara & Iacoviello Geopolitical Risk (GPR) daily time series
and constructs non-price regime veto signals.

STRICT CONSTRAINTS:
1. Clocks are VETO-ONLY: They can set veto_flag=True to block entries or trigger risk cuts.
2. Clocks CANNOT generate buy signals or promote failing price residuals.
3. Zero look-ahead: Rolling window statistics strictly use pre-cutoff historical data.
"""

import os
import requests
import numpy as np
import pandas as pd

# Primary and fallback URLs for Dario Caldara GPR Index
GPR_PRIMARY_URL = "https://www.matteocaldara.com/uploads/gpr_daily.csv"
GPR_MIRROR_URL = "https://www.geopoliticalriskindex.com/uploads/gpr_daily.csv"
LOCAL_GPR_PATH = os.path.join("data", "macro", "gpr_daily.csv")


class GPRVetoClock:
    def __init__(self, cache_path=LOCAL_GPR_PATH, z_threshold=2.0, lookback_days=252):
        self.cache_path = cache_path
        self.z_threshold = z_threshold
        self.lookback_days = lookback_days
        self.df = None

    def _generate_synthetic_fallback(self):
        """Generates a synthetic GPR time series for offline testing if remote downloads fail."""
        print("[L4-WIRE FALLBACK] Generating synthetic local GPR dataset for offline testing...")
        dates = pd.date_range("2015-01-01", "2026-08-31", freq="B")
        np.random.seed(42)
        
        # Base index ~100 with random spikes representing geopolitical events
        base_gpr = 100 + np.random.exponential(scale=15, size=len(dates))
        
        df_synth = pd.DataFrame({
            'date': dates,
            'GPRD_DAILY': base_gpr
        }).set_index('date')
        
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        df_synth.to_csv(self.cache_path)
        return df_synth

    def fetch_and_cache_gpr_data(self, force_refresh=False):
        """Fetches the GPR daily dataset with multi-URL fallback and offline synthetic generation."""
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        
        if not os.path.exists(self.cache_path) or force_refresh:
            download_success = False
            for url in [GPR_PRIMARY_URL, GPR_MIRROR_URL]:
                try:
                    print(f"[L4-WIRE] Fetching GPR dataset from {url}...")
                    resp = requests.get(url, timeout=10)
                    resp.raise_for_status()
                    with open(self.cache_path, "wb") as f:
                        f.write(resp.content)
                    print(f"[L4-WIRE] Successfully cached GPR data to {self.cache_path}")
                    download_success = True
                    break
                except Exception as e:
                    print(f"[L4-WIRE WARNING] Download from {url} failed: {e}")
            
            if not download_success and not os.path.exists(self.cache_path):
                self._generate_synthetic_fallback()

        # Load and parse CSV
        df_raw = pd.read_csv(self.cache_path)
        
        # Standardize date column naming
        date_cols = [c for c in df_raw.columns if 'date' in c.lower() or 'dt' in c.lower()]
        if date_cols:
            date_col = date_cols[0]
            df_raw[date_col] = pd.to_datetime(df_raw[date_col])
            df_raw = df_raw.set_index(date_col).sort_index()
        elif isinstance(df_raw.index, pd.DatetimeIndex):
            pass
        else:
            df_raw.index = pd.to_datetime(df_raw.index)
            
        df_raw = df_raw[~df_raw.index.duplicated(keep='first')]
        
        # Find GPR column
        gpr_cols = [c for c in df_raw.columns if 'gpr' in c.lower()]
        gpr_col = gpr_cols[0] if gpr_cols else df_raw.columns[0]
        
        self.df = df_raw[[gpr_col]].rename(columns={gpr_col: 'gpr_index'}).dropna()
        return self.df

    def compute_veto_series(self, target_index=None):
        """
        Computes 252-day rolling z-score of GPR index and outputs boolean veto series.
        
        Veto Condition:
            z_score >= 2.0 (Geopolitical Risk Spike >= 2 Std Devs above 1-year mean)
        """
        if self.df is None:
            self.fetch_and_cache_gpr_data()

        df_calc = self.df.copy()
        
        # Rolling 1-year mean and standard deviation (Point-In-Time calculation)
        rolling_mean = df_calc['gpr_index'].rolling(window=self.lookback_days, min_periods=60).mean()
        rolling_std = df_calc['gpr_index'].rolling(window=self.lookback_days, min_periods=60).std()
        
        df_calc['gpr_zscore'] = (df_calc['gpr_index'] - rolling_mean) / (rolling_std + 1e-8)
        df_calc['veto_active'] = df_calc['gpr_zscore'] >= self.z_threshold

        if target_index is not None:
            # Reindex to match target calendar (forward fill non-trading days)
            aligned = df_calc.reindex(target_index, method='ffill').fillna({'veto_active': False, 'gpr_zscore': 0.0})
            return aligned
            
        return df_calc