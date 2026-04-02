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
    
    # --- ML Point-in-Time Features ---
    score: int = 0
    beta_aspi: Optional[float] = None
    market_cap: float = 0.0
    cv_10: float = 0.0

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
    score: int = 0
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


@dataclass
class RunStats:
    run_date: str
    trading_day: bool
    top10_count: int = 0
    tracked_stocks_fetched: int = 0
    new_stocks_added_to_track: int = 0
    candidates_count: int = 0
    whitelisted_added: int = 0
    churned: int = 0

    def to_dict(self):
        return asdict(self)