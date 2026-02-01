from .metrics import mean, cv , min_

def evaluate(record, settings):
    H = record.history
    if len(H) < 3:   #settings.window_trading_days
        return None

    trades = [h.trade_volume for h in H]
    turnover = [h.turnover for h in H]
    appearances = sum(h.in_top10 for h in H)
    hard_pass = (
        appearances >= settings.min_top10_appearances_in_window and
        cv(trades) <= settings.trade_cv_max and
        mean(turnover) >= settings.turnover_threshold_lkr
    )

    r = mean(turnover)/settings.turnover_threshold_lkr
    turnover_pts = min_(r)
    appearances_pts = 6.0*(appearances/settings.window_trading_days)
    beta_ok = record.static.beta_aspi is not None
    score = round(turnover_pts) + round(appearances_pts)

    return hard_pass, beta_ok, score, mean(turnover)
