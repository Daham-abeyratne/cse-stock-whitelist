import argparse
from pathlib import Path
from .settings import load_settings
from .market.calendar import load_calendar
from .market.cse_client import CSEClient
from .market.index_client import IndexClient
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
    
    # Fetch Index Data
    if calendar.is_trading_day(d):
        try:
            import json
            idx_client = IndexClient()
            idx_data = idx_client.fetch_index_summary(d)
            idx_file = Path(a.data_dir) / "index_history.json"
            
            history = []
            if idx_file.exists():
                with open(idx_file, "r", encoding="utf-8") as f:
                    try:
                        history = json.load(f)
                    except json.JSONDecodeError:
                        pass
            
            # Remove existing entry for same day
            history = [h for h in history if h.get("date") != d.isoformat()]
            
            history.append({
                "date": d.isoformat(),
                "aspi": idx_data.get("ASPI", 0.0),
                "sp_sl20": idx_data.get("S&P SL20", 0.0)
            })
            
            # Keep last 100 days
            history.sort(key=lambda x: x["date"])
            history = history[-100:]
            
            with open(idx_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to fetch/save index data: {e}")

if __name__ == "__main__":
    main()
