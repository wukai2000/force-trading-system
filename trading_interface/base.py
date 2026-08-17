"""
Swappable trading interface.

Concrete backends:
- python_sim (current default)
- ibkr_paper (future)
- robinhood_agentic (future)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIAL = "partial"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    SIMULATED = "simulated"


@dataclass
class OrderRequest:
    symbol: str
    side: OrderSide
    quantity: float
    order_type: str = "market"  # market | limit
    limit_price: Optional[float] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrderResult:
    request: OrderRequest
    status: OrderStatus
    filled_quantity: float = 0.0
    avg_fill_price: float = 0.0
    message: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.request.symbol,
            "side": self.request.side.value,
            "quantity": self.request.quantity,
            "status": self.status.value,
            "filled_quantity": self.filled_quantity,
            "avg_fill_price": self.avg_fill_price,
            "message": self.message,
        }


class TradingInterface(ABC):
    """Common interface every backend must implement."""

    name: str = "base"

    @abstractmethod
    def get_cash(self) -> float:
        ...

    @abstractmethod
    def get_positions(self) -> Dict[str, float]:
        """symbol → quantity"""
        ...

    @abstractmethod
    def submit_order(self, order: OrderRequest) -> OrderResult:
        ...

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        ...

    def summary(self) -> Dict[str, Any]:
        return {
            "interface": self.name,
            "cash": self.get_cash(),
            "positions": self.get_positions(),
        }
