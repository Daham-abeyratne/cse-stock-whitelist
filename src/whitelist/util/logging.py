from dataclasses import dataclass, asdict

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

