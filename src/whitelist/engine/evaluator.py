from .metrics import mean, cv, min_

def evaluate(record, settings):
    H = record.history
    
    # Fast Start: Begin evaluating as soon as we have 3 days of history
    if len(H) < 3: 
        return None

    trades = [h.trade_volume for h in H]
    turnover = [h.turnover for h in H]
    appearances = sum(h.in_top10 for h in H)
    
    # --- SWING MOMENTUM (10-Day Lookback) ---
    # Current close must be >= the close 10 days ago (or start of history if < 10)
    lookback = max(0, len(H) - 10)
    price_trend_ok = H[-1].close >= H[lookback].close
    
    # Dynamic Liquidity Floor
    market_cap_floor = record.static.market_cap * 0.0005
    dynamic_turnover_threshold = max(settings.turnover_threshold_lkr, market_cap_floor)

    # Hard Rules (Pass/Fail)
    hard_pass = (
        appearances >= settings.min_top10_appearances_in_window and
        cv(trades) <= settings.trade_cv_max and
        mean(turnover) >= dynamic_turnover_threshold and
        price_trend_ok
    )

    # Static Filters (Market Cap & Beta)
    market_cap_ok = record.static.market_cap >= settings.market_cap_min_lkr
    
    beta_val = record.static.beta_aspi
    beta_in_range = (
        beta_val is not None and 
        settings.beta_lower <= beta_val <= settings.beta_upper
    )

    # Scoring Logic (0-10 Scale)
    r = mean(turnover) / settings.turnover_threshold_lkr
    turnover_pts = min_(r)
    
    # Appearance points: Scaled to 6.0 based on current history length
    appearances_pts = 6.0 * (appearances / len(H))
    
    # Momentum Bonus: 1 point for closing within 5% of the 10-DAY high
    recent_high = max(h.high for h in H[lookback:])
    momentum_bonus = 1.0 if H[-1].close >= (recent_high * 0.95) else 0.0
    
    score = round(turnover_pts) + round(appearances_pts) + round(momentum_bonus)

    # Eligibility check includes the Beta missing logic flag
    is_eligible = (
        hard_pass and 
        market_cap_ok and 
        (not settings.beta_missing_blocks_promotion or beta_in_range)
    )

    return is_eligible, beta_in_range, score, mean(turnover)