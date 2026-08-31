from dataclasses import dataclass
from pathlib import Path

from .storage.json_store import read_json
from .util.errors import ConfigError


@dataclass(frozen=True)
class Settings:
    data_dir: Path

    # History & Appearances
    window_trading_days: int
    min_top10_appearances_in_window: int

    # Liquidity & Volatility
    trade_cv_max: float
    turnover_threshold_lkr: float

    # Market Cap
    market_cap_min_lkr: float

    # Beta Filters
    beta_lower: float
    beta_upper: float
    beta_required_for_whitelist: bool
    beta_required_for_candidate: bool

    # Price Range Limits
    range_ratio_min: float
    range_ratio_max_extreme: float
    extreme_days_max: int

    # Scoring Thresholds
    whitelist_min_score: int
    candidate_min_score: int

    # Churn / Exit Rules
    churn_fail_hard_n: int
    churn_low_turn_n: int
    
    # Optimizations
    static_refresh_interval_days: int


def load_settings(data_dir: Path) -> Settings:
    cfg_path = data_dir / "config.json"
    if not cfg_path.exists():
        raise ConfigError(f"Missing config.json at {cfg_path}")

    cfg = read_json(cfg_path)

    try:
        beta_limits = cfg.get("beta_limits", {})
        return Settings(
            data_dir=data_dir,

            # General Window Settings
            window_trading_days=int(cfg["window_trading_days"]),
            min_top10_appearances_in_window=int(cfg["min_top10_appearances_in_window"]),

            # Hard Rules: Turnover & Volatility
            trade_cv_max=float(cfg["trade_cv_max"]),
            turnover_threshold_lkr=float(cfg["turnover_threshold_lkr"]),

            # Market Cap
            market_cap_min_lkr=float(cfg["market_cap_min_lkr"]),

            # Beta
            beta_lower=float(beta_limits.get("lower", 0.0)),
            beta_upper=float(beta_limits.get("upper", 2.5)),
            beta_required_for_whitelist=bool(cfg.get("beta_required_for_whitelist", True)),
            beta_required_for_candidate=bool(cfg.get("beta_required_for_candidate", False)),

            # Price Range Ratio
            range_ratio_min=float(cfg["range_ratio_limits"]["min"]),
            range_ratio_max_extreme=float(cfg["range_ratio_limits"]["max_extreme"]),
            extreme_days_max=int(cfg["range_ratio_limits"]["extreme_days_max"]),

            # Scoring
            whitelist_min_score=int(cfg["scoring"]["whitelist_min_score"]),
            candidate_min_score=int(cfg["scoring"]["candidate_min_score"]),

            # Churn
            churn_fail_hard_n=int(cfg["churn"].get("remove_if_fail_hard_rules_consecutive", 3)),
            churn_low_turn_n=int(cfg["churn"].get("remove_if_avg_turnover_below_threshold_consecutive", 5)),
            
            # Optimizations
            static_refresh_interval_days=int(cfg.get("static_refresh_interval_days", 7))
        )

    except KeyError as e:
        raise ConfigError(f"Missing required key in config.json: {e}") from e
    except ValueError as e:
        raise ConfigError(f"Invalid data type in config.json: {e}") from e