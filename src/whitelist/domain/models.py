from dataclasses import dataclass, field, asdict
from typing import Optional
from .types import Status

@dataclass
class HistoryRow:
    date: str
    in_top10: bool
    turnover: float
    share_volume: float
    trade_volume: float
    high: float
    low: float
    close: float

@dataclass
class StockStatic:
    market_cap: float = 0.0
    beta_aspi: Optional[float] = None
    beta_sl20: Optional[float] = None
    last_static_update: Optional[str] = None

@dataclass
class StockState:
    status: Status = Status.TRACK
    first_seen: str = ""
    last_updated: str = ""
    candidated_on: Optional[str] = None
    whitelisted_on: Optional[str] = None
    churned_on: Optional[str] = None
    fail_hard_rules_consecutive: int = 0
    avg_turnover_below_threshold_consecutive: int = 0

@dataclass
class StockRecord:
    symbol: str
    state: StockState
    static: StockStatic = field(default_factory=StockStatic)
    history: list[HistoryRow] = field(default_factory=list)

    def append_history(self, row: HistoryRow):
        self.history = [h for h in self.history if h.date != row.date]
        self.history.append(row)
        self.history.sort(key=lambda x: x.date)

    def trim_history(self, keep_dates: set[str]):
        self.history = [h for h in self.history if h.date in keep_dates]
