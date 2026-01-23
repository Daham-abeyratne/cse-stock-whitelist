import argparse
from pathlib import Path
from .settings import load_settings
from .market.calendar import load_calendar
from .market.cse_client import CSEClient
from .storage.repositories import StockRepository, DailyRepository, OutputRepository
from .storage.paths import DataPaths
from .engine.pipeline import Pipeline
from .util.timeutils import today_colombo, parse_iso_date
from .util.logging import RunStats

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", default="data")
    p.add_argument("--date", default=None)
    a = p.parse_args()

    d = parse_iso_date(a.date) if a.date else today_colombo()
    settings = load_settings(Path(a.data_dir))
    calendar = load_calendar(settings.data_dir)

    repo = StockRepository(DataPaths(settings.data_dir))
    client = CSEClient()

    paths = DataPaths(settings.data_dir)

    stock_repo = StockRepository(paths)
    daily_repo = DailyRepository(paths)
    output_repo = OutputRepository(paths)

    pipeline = Pipeline(settings, calendar,client, stock_repo, daily_repo, output_repo)
    pipeline.run(d, RunStats(d.isoformat(), calendar.is_trading_day(d)))

if __name__ == "__main__":
    main()
