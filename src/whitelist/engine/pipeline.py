from ..domain.models import HistoryRow, StockRecord, StockState
from ..domain.types import Status
from ..util.timeutils import iso
from .evaluator import evaluate
from .transitions import apply_transition

class Pipeline:
    def __init__(self, settings, calendar, client, stock_repo, daily_repo, output_repo):
        self.settings = settings
        self.calendar = calendar
        self.client = client
        self.repo = stock_repo
        self.daily_repo = daily_repo
        self.output_repo = output_repo

    def run(self, d, runstats):
        if not self.calendar.is_trading_day(d):
            return

        day_iso = iso(d)
        records = self.repo.load_all()
        top10, top10_metrics = self.client.fetch_top10_snapshot(d)
        keep = {iso(x) for x in self.calendar.last_n_trading_days(d, self.settings.window_trading_days)}

        fetch_set = set(top10) | {s for s, r in records.items() if r.state.status != Status.CHURNED}


        # --- write daily snapshot (raw evidence for the day) ---
        if self.daily_repo is not None:
            self.daily_repo.save_day_snapshot(day_iso, {
                "date": day_iso,
                "top10_symbols": top10,
                "mostActiveTrades_raw_by_symbol": top10_metrics
            })

        for sym in fetch_set:
            rec = records.get(sym) or StockRecord(sym, StockState(first_seen=day_iso))
            rec.state.last_updated = day_iso

            daily = self.client.fetch_daily_metrics(sym, d)

            raw = top10_metrics.get(sym, {}) if (sym in top10) else {}

            turnover = float(raw.get("turnover", 0.0) or 0.0) if (sym in top10) else daily.turnover
            trade_volume = float(raw.get("tradeVolume", 0.0) or 0.0) if (sym in top10) else daily.trade_volume
            share_volume = float(raw.get("shareVolume", 0.0) or 0.0) if (sym in top10) else daily.share_volume

            rec.append_history(HistoryRow(
                date=day_iso,
                in_top10=(sym in top10),
                turnover=turnover,
                share_volume=share_volume,
                trade_volume=trade_volume,
                high=daily.high,
                low=daily.low,
                close=daily.close
            ))
            rec.trim_history(keep)
            evalr = evaluate(rec, self.settings)
            if evalr:
                apply_transition(rec, evalr, d, self.settings)

            # --- static refresh: fetch once if missing ---
            needs_static = (
                rec.static.market_cap == 0.0
                and rec.static.beta_aspi is None
                and rec.static.beta_sl20 is None
            )

            if needs_static:
                sm = self.client.fetch_static_metrics(sym, d)
                rec.static.market_cap = sm.market_cap
                rec.static.beta_aspi = sm.beta_aspi
                rec.static.beta_sl20 = sm.beta_sl20
                rec.static.last_static_update = day_iso

            self.repo.save(rec)

        # --- write outputs (consumable summaries for UI) ---
        if self.output_repo is not None:
            all_records = self.repo.load_all()

            whitelist = []
            candidates = []

            for sym, r in all_records.items():
                if r.state.status == Status.WHITELIST:
                    whitelist.append({
                        "symbol": sym,
                        "whitelisted_on": r.state.whitelisted_on,
                        "market_cap": r.static.market_cap,
                        "beta_aspi": r.static.beta_aspi,
                        "beta_sl20": r.static.beta_sl20
                    })
                elif r.state.status == Status.CANDIDATE:
                    candidates.append({
                        "symbol": sym,
                        "days_in_window": len(r.history),
                        "top10_appearances": sum(h.in_top10 for h in r.history)
                    })

            self.output_repo.save_whitelist_latest({
                "as_of": day_iso,
                "whitelist": sorted(whitelist, key=lambda x: x["symbol"])
            })

            self.output_repo.save_candidates_latest({
                "as_of": day_iso,
                "candidates": sorted(candidates, key=lambda x: x["symbol"])
            })

            # update runstats if you want (optional)
            runstats.top10_count = len(top10)

            self.output_repo.save_runlog_latest(runstats.to_dict())