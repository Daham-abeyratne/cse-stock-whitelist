from .metrics import mean, cv

def evaluate(record, settings):
    H = record.history
    if len(H) < settings.window_trading_days:
        return None

    trades = [h.trade_volume for h in H]
    turnover = [h.turnover for h in H]
    appearances = sum(h.in_top10 for h in H)

    hard_pass = (
        appearances >= settings.min_top10_appearances_in_window and
        cv(trades) <= settings.trade_cv_max and
        mean(turnover) >= settings.turnover_threshold_lkr
    )

    beta_ok = record.static.beta_aspi is not None
    score = 1 if hard_pass else 0

    return hard_pass, beta_ok, score, mean(turnover)
