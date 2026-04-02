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

    # Trade Value Limits
    avg_trade_value_lower: float
    avg_trade_value_upper: float

    # Market Cap
    market_cap_min_lkr: float

    # Beta Filters
    beta_lower: float
    beta_upper: float
    beta_missing_blocks_promotion: bool  # Moved to a required field for explicit config

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


def load_settings(data_dir: Path) -> Settings:
    cfg_path = data_dir / "config.json"
    if not cfg_path.exists():
        raise ConfigError(f"Missing config.json at {cfg_path}")

    cfg = read_json(cfg_path)

    try:
        return Settings(
            data_dir=data_dir,

            # General Window Settings
            window_trading_days=int(cfg["window_trading_days"]),
            min_top10_appearances_in_window=int(cfg["min_top10_appearances_in_window"]),

            # Hard Rules: Turnover & Volatility
            trade_cv_max=float(cfg["trade_cv_max"]),
            turnover_threshold_lkr=float(cfg["turnover_threshold_lkr"]),

            # Average Trade Value (Nested in limits_lkr)
            avg_trade_value_lower=float(cfg["avg_trade_value_limits_lkr"]["lower"]),
            avg_trade_value_upper=float(cfg["avg_trade_value_limits_lkr"]["upper"]),

            # Market Cap
            market_cap_min_lkr=float(cfg["market_cap_min_lkr"]),

            # Beta (Nested in beta_limits)
            beta_lower=float(cfg["beta_limits"]["lower"]),
            beta_upper=float(cfg["beta_limits"]["upper"]),
            
            # Logic Flag: If Beta is missing, should we block promotion? 
            # Note: If this key is missing in your JSON, it defaults to True.
            beta_missing_blocks_promotion=bool(cfg.get("beta_missing_blocks_promotion", True)),

            # Price Range Ratio (Nested in range_ratio_limits)
            range_ratio_min=float(cfg["range_ratio_limits"]["min"]),
            range_ratio_max_extreme=float(cfg["range_ratio_limits"]["max_extreme"]),
            extreme_days_max=int(cfg["range_ratio_limits"]["extreme_days_max"]),

            # Scoring (Nested in scoring)
            whitelist_min_score=int(cfg["scoring"]["whitelist_min_score"]),
            candidate_min_score=int(cfg["scoring"]["candidate_min_score"]),

            # Churn (Nested in churn)
            churn_fail_hard_n=int(cfg["churn"]["remove_if_fail_hard_rules_consecutive"]),
            churn_low_turn_n=int(cfg["churn"]["remove_if_avg_turnover_below_threshold_consecutive"]),
        )

    except KeyError as e:
        raise ConfigError(f"Missing required key in config.json: {e}") from e
    except ValueError as e:
        raise ConfigError(f"Invalid data type in config.json: {e}") from e