"""
Signature / filter helpers.

Each force may need its own filter to make the historical pattern visible.
These are placeholders that will be replaced by data-driven signature discovery.
"""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd


def identity_filter(series: pd.Series) -> pd.Series:
    """No-op filter (placeholder)."""
    return series


def relative_strength(series: pd.Series, benchmark: pd.Series) -> pd.Series:
    """Simple relative strength vs a benchmark."""
    return series / benchmark


# Registry of known signature functions (expand as we discover real filters)
SIGNATURE_REGISTRY = {
    "identity": identity_filter,
    "relative_strength": relative_strength,
}


def apply_signature(name: str, data: Dict[str, Any], **kwargs) -> Any:
    """Apply a named signature if registered; otherwise return data unchanged."""
    fn = SIGNATURE_REGISTRY.get(name)
    if fn is None:
        return data
    return fn(**kwargs) if kwargs else data
