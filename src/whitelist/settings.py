from dataclasses import dataclass
from pathlib import Path

from .storage.json_store import read_json
from .util.errors import ConfigError


@dataclass(frozen=True)
class Settings:
    data_dir: Path

    window_trading_days: int
    min_top10_appearances_in_window: int

    trade_cv_max: float
    turnover_threshold_lkr: float

    avg_trade_value_lower: float
    avg_trade_value_upper: float

    market_cap_min_lkr: float

    beta_lower: float
    beta_upper: float

    range_ratio_min: float
    range_ratio_max_extreme: float
    extreme_days_max: int

    whitelist_min_score: int

    churn_fail_hard_n: int
    churn_low_turn_n: int

    # OPTION B FLAG (important)
    beta_missing_blocks_promotion: bool = True


def load_settings(data_dir: Path) -> Settings:
    cfg_path = data_dir / "config.json"
    if not cfg_path.exists():
        raise ConfigError(f"Missing config.json at {cfg_path}")

    cfg = read_json(cfg_path)

    try:
        return Settings(
            data_dir=data_dir,

            window_trading_days=int(cfg["window_trading_days"]),
            min_top10_appearances_in_window=int(cfg["min_top10_appearances_in_window"]),

            trade_cv_max=float(cfg["trade_cv_max"]),
            turnover_threshold_lkr=float(cfg["turnover_threshold_lkr"]),

            avg_trade_value_lower=float(cfg["avg_trade_value_limits_lkr"]["lower"]),
            avg_trade_value_upper=float(cfg["avg_trade_value_limits_lkr"]["upper"]),

            market_cap_min_lkr=float(cfg["market_cap_min_lkr"]),

            beta_lower=float(cfg["beta_limits"]["lower"]),
            beta_upper=float(cfg["beta_limits"]["upper"]),

            range_ratio_min=float(cfg["range_ratio_limits"]["min"]),
            range_ratio_max_extreme=float(cfg["range_ratio_limits"]["max_extreme"]),
            extreme_days_max=int(cfg["range_ratio_limits"]["extreme_days_max"]),

            whitelist_min_score=int(cfg["scoring"]["whitelist_min_score"]),

            churn_fail_hard_n=int(cfg["churn"]["remove_if_fail_hard_rules_consecutive"]),
            churn_low_turn_n=int(cfg["churn"]["remove_if_avg_turnover_below_threshold_consecutive"]),
        )

    except KeyError as e:
        raise ConfigError(f"Missing key in config.json: {e}") from e
