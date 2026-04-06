from .metrics import mean, cv, min_

def evaluate(record, settings):
    H = record.history
    
    # Fast Start: Begin evaluating as soon as we have 3 days of history
    if len(H) < 3: 
        return None

    def wick_ratio(h):
        return (h.close - h.low) / (h.high - h.low + 0.0001)

    trades = [h.trade_volume for h in H]
    turnover = [h.turnover for h in H]
    appearances = sum(h.in_top10 for h in H)
    
    # --- SWING MOMENTUM (10-Day Lookback) ---
    # Current close must be >= the close 10 days ago (or start of history if < 10)
    lookback = max(0, len(H) - 10)
    price_trend_ok = H[-1].close >= H[lookback].close
    
    recent_10_h = H[lookback:]
    recent_10_high = max((h.high for h in recent_10_h), default=0.0)
    recent_10_low = min((h.low for h in recent_10_h), default=0.0)
    
    # --- PRE-BREAKOUT METRICS ---
    # 1. Wick Analysis (Accumulation)
    last_3_wicks = [wick_ratio(h) for h in H[-3:]]
    avg_wick = sum(last_3_wicks) / len(last_3_wicks) if last_3_wicks else 0.0
    accumulation_bonus = 1.0 if avg_wick > 0.6 else 0.0

    # 2. VCP Contraction
    range_10_pct = (recent_10_high - recent_10_low) / (H[-1].close + 0.0001)
    close_to_high_ratio = H[-1].close / (recent_10_high + 0.0001)
    coiling_bonus = 2.0 if (range_10_pct < 0.05 and close_to_high_ratio > 0.95) else 0.0
    
    # Dynamic Liquidity Floor
    market_cap_floor = record.static.market_cap * 0.0005
    dynamic_turnover_threshold = max(settings.turnover_threshold_lkr, market_cap_floor)

    # 3. Distribution Penalty
    avg_turnover = mean(turnover)
    turnover_ratio = avg_turnover / (dynamic_turnover_threshold + 0.0001)
    today_wick = wick_ratio(H[-1])
    is_distributing = (turnover_ratio > 2.5) and (today_wick < 0.25)

    # Hard Rules (Pass/Fail)
    hard_pass = (
        not is_distributing and
        appearances >= settings.min_top10_appearances_in_window and
        cv(trades) <= settings.trade_cv_max and
        avg_turnover >= dynamic_turnover_threshold and
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
    r = avg_turnover / settings.turnover_threshold_lkr
    turnover_pts = min_(r)
    
    # Appearance points: Scaled to 6.0 based on current history length
    appearances_pts = 6.0 * (appearances / len(H))
    
    score = round(turnover_pts) + round(appearances_pts) + round(accumulation_bonus) + round(coiling_bonus)

    # Eligibility check includes the Beta missing logic flag
    is_eligible = (
        hard_pass and 
        market_cap_ok and 
        (not settings.beta_missing_blocks_promotion or beta_in_range)
    )

    return is_eligible, beta_in_range, score, mean(turnover)