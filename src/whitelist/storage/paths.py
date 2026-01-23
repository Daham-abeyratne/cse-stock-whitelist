from pathlib import Path

class DataPaths:
    def __init__(self, base: Path):
        self.base = base

    def stocks_dir(self): return self.base / "stocks"
    def daily_dir(self): return self.base / "daily"
    def outputs_dir(self): return self.base / "outputs"

    def stock(self, symbol): return self.stocks_dir() / f"{symbol}.json"
    def daily(self, d): return self.daily_dir() / f"{d}.json"
    def whitelist(self): return self.outputs_dir() / "whitelist_latest.json"
    def candidates(self): return self.outputs_dir() / "candidates_latest.json"
    def runlog(self): return self.outputs_dir() / "run_log_latest.json"
