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
