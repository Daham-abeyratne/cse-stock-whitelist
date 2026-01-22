from datetime import date, timedelta
from pathlib import Path
from ..storage.json_store import read_json

class TradingCalendar:
    def __init__(self, holidays: set[date]):
        self.holidays = holidays

    def is_trading_day(self, d: date):
        return d.weekday() < 5 and d not in self.holidays

    def last_n_trading_days(self, end: date, n: int):
        days = []
        cur = end
        while len(days) < n:
            if self.is_trading_day(cur):
                days.append(cur)
            cur -= timedelta(days=1)
        return list(reversed(days))

def load_calendar(data_dir: Path):
    data = read_json(data_dir / "calendar.json")
    return TradingCalendar({date.fromisoformat(x) for x in data.get("holidays", [])})
