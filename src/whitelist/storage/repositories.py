from .json_store import read_json, write_json_atomic
from ..domain.models import StockRecord, StockState, StockStatic, HistoryRow
from .paths import DataPaths

class StockRepository:
    def __init__(self, paths: DataPaths):
        self.paths = paths
        self.paths.stocks_dir().mkdir(parents=True, exist_ok=True)

    def load_all(self):
        out = {}
        for p in self.paths.stocks_dir().glob("*.json"):
            d = read_json(p)
            out[d["symbol"]] = StockRecord(
                symbol=d["symbol"],
                state=StockState(**d["state"]),
                static=StockStatic(**d["static"]),
                history=[HistoryRow(**{k: v for k, v in h.items() if k != "trade_count"}) for h in d.get("history", [])],
            )
        return out

    def save(self, record: StockRecord):
        write_json_atomic(self.paths.stock(record.symbol), {
            "symbol": record.symbol,
            "state": record.state.__dict__,
            "static": record.static.__dict__,
            "history": [h.__dict__ for h in record.history],
        })

class DailyRepository:
    def __init__(self, paths):
        self.paths = paths
        self.paths.daily_dir().mkdir(parents=True, exist_ok=True)

    def save_day_snapshot(self, day_iso: str, payload: dict):
        write_json_atomic(self.paths.daily(day_iso), payload)

class OutputRepository:
    def __init__(self, paths):
        self.paths = paths
        self.paths.outputs_dir().mkdir(parents=True, exist_ok=True)

    def save_whitelist_latest(self, payload: dict):
        write_json_atomic(self.paths.whitelist(), payload)

    def save_candidates_latest(self, payload: dict):
        write_json_atomic(self.paths.candidates(), payload)

    def save_runlog_latest(self, payload: dict):
        write_json_atomic(self.paths.runlog(), payload)
