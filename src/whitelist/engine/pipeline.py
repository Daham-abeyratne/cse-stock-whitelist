from ..domain.models import HistoryRow, StockRecord, StockState
from ..domain.types import Status
from ..util.timeutils import iso
from ..util.errors import PipelineError
from ..util.instrument import get_instrument_type
from .evaluator import evaluate
from .transitions import apply_transition
from .metrics import cv  # NEW: We need this to calculate the 10-day CV for ML
from .validation import validate_daily_bar
from datetime import datetime

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
        
        if len(top10) == 0:
            print(f"Notice: CSE top 10 snapshot returned 0 symbols for {day_iso} (market may be closed or pre-market). Processing existing tracked stocks.")
        elif len(top10) < 10:
            print(f"Notice: Got {len(top10)} top symbols from CSE API.")
        
        keep = {iso(x) for x in self.calendar.last_n_trading_days(d, self.settings.window_trading_days)}
        cool_down_keep = {iso(x) for x in self.calendar.last_n_trading_days(d, 20)}

        fetch_set = set(top10)
        for sym, r in records.items():
            if r.state.status != Status.CHURNED:
                fetch_set.add(sym)
            elif r.state.churned_on and r.state.churned_on in cool_down_keep:
                fetch_set.add(sym)
                
        if len(fetch_set) == 0:
            print("Notice: No symbols available to fetch for today.")
            return

        if self.daily_repo is not None:
            self.daily_repo.save_day_snapshot(day_iso, {
                "date": day_iso,
                "top10_symbols": top10,
                "mostActiveTrades_raw_by_symbol": top10_metrics
            })

        for sym in fetch_set:
            if sym not in records:
                runstats.new_stocks_added_to_track += 1
            
            rec = records.get(sym) or StockRecord(sym, StockState(first_seen=day_iso))
            runstats.tracked_stocks_fetched += 1

            if rec.state.status == Status.CHURNED and sym in top10:
                rec.state.status = Status.TRACK
                rec.state.churned_on = None
                rec.state.fail_hard_rules_consecutive = 0
                rec.state.avg_turnover_below_threshold_consecutive = 0
            
            daily = self.client.fetch_daily_metrics(sym, d)
            raw = top10_metrics.get(sym, {}) if (sym in top10) else {}
            
            # Instrument tagging
            rec.static.instrument_type = get_instrument_type(sym)
            
            # --- FETCH STATIC EARLY (Interval based) --- 
            needs_static = True
            if rec.static.last_static_update:
                try:
                    last_update = datetime.fromisoformat(rec.static.last_static_update)
                    days_since = (datetime.fromisoformat(day_iso) - last_update).days
                    if days_since < self.settings.static_refresh_interval_days:
                        needs_static = False
                except ValueError:
                    pass
            
            if needs_static:
                sm = self.client.fetch_static_metrics(sym, d)
                rec.static.market_cap = sm.market_cap
                rec.static.beta_aspi = sm.beta_aspi
                rec.static.beta_sl20 = sm.beta_sl20
                rec.static.last_static_update = day_iso

            turnover = float(raw.get("turnover", 0.0) or 0.0) if (sym in top10) else daily.turnover
            trade_volume = float(raw.get("tradeVolume", 0.0) or 0.0) if (sym in top10) else daily.trade_volume
            share_volume = float(raw.get("shareVolume", 0.0) or 0.0) if (sym in top10) else daily.share_volume
            
            # Validate bar
            if not validate_daily_bar(daily.high, daily.low, daily.close, rec.static.instrument_type):
                continue

            # Append the basic price row first
            rec.append_history(HistoryRow(
                date=day_iso,
                in_top10=(sym in top10),
                turnover=turnover,
                share_volume=share_volume,
                trade_volume=trade_volume,
                high=daily.high,
                low=daily.low,
                close=daily.close,
                previous_close=daily.previous_close,
                change_percentage=daily.change_percentage
            ))
            rec.trim_history(keep)

            # Evaluate using today's appended price and static data
            old_status = rec.state.status
            evalr = evaluate(rec, self.settings)
            
            current_score = 0
            if evalr:
                hard_pass, is_low_turnover, beta_ok, score = evalr
                current_score = score
                rec.state.score = score
                apply_transition(rec, evalr, d, self.settings)

            if old_status != rec.state.status:
                if rec.state.status == Status.WHITELIST:
                    runstats.whitelisted_added += 1
                elif rec.state.status == Status.CHURNED:
                    runstats.churned += 1

            # --- SNAPSHOT THE ML FEATURES ---
            # Calculate the 10-day volatility specifically for the ML model
            trades_10 = [h.trade_volume for h in rec.history[-10:]]
            cv_10_val = cv(trades_10) if len(trades_10) > 1 else 0.0
            
            # Turnover Ratio
            market_cap_floor = rec.static.market_cap * 0.0001
            dynamic_turnover_threshold = max(self.settings.turnover_threshold_lkr, market_cap_floor)
            turnover_10_mean = sum(h.turnover for h in rec.history) / len(rec.history) if rec.history else 0.0
            turnover_ratio = turnover_10_mean / dynamic_turnover_threshold if dynamic_turnover_threshold else 0.0

            # Momentum Ratio
            lookback = max(0, len(rec.history) - 10)
            recent_high = max((h.high for h in rec.history[lookback:]), default=0.0)
            momentum_ratio = rec.history[-1].close / recent_high if recent_high > 0 else 0.0

            # Update the row we just appended with the Point-in-Time metrics
            rec.history[-1].score = current_score
            rec.history[-1].beta_aspi = rec.static.beta_aspi
            rec.history[-1].market_cap = rec.static.market_cap
            rec.history[-1].cv_10 = round(cv_10_val, 4)
            rec.history[-1].turnover_ratio = round(turnover_ratio, 4)
            rec.history[-1].momentum_ratio = round(momentum_ratio, 4)

            self.repo.save(rec)

        # --- WRITE OUTPUTS (Consumable summaries for UI) ---
        if self.output_repo is not None:
            all_records = self.repo.load_all()
            whitelist = []
            candidates = []

            for sym, r in all_records.items():
                if r.state.status == Status.WHITELIST:
                    whitelist.append({
                        "symbol": sym,
                        "score": r.state.score,
                        "whitelisted_on": r.state.whitelisted_on,
                        "market_cap": r.static.market_cap,
                        "beta_aspi": r.static.beta_aspi
                    })
                elif r.state.status == Status.CANDIDATE:
                    candidates.append({
                        "symbol": sym,
                        "score": r.state.score,
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

            runstats.candidates_count = len(candidates)
            runstats.top10_count = len(top10)
            self.output_repo.save_runlog_latest(runstats.to_dict())