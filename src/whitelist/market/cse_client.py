import requests, json
from dataclasses import dataclass
from typing import Optional
from ..util.errors import FetchError

@dataclass(frozen=True)
class DailyMetrics:
    turnover: float
    share_volume: float
    trade_volume: float
    high: float
    low: float
    close: float
    previous_close: float
    change_percentage: float

@dataclass(frozen=True)
class StaticMetrics:
    market_cap: float
    beta_aspi: Optional[float]
    beta_sl20: Optional[float]

class CSEClient:
    BASE = "https://www.cse.lk/api"

    def __init__(self):
        self.s = requests.Session()

    def _post_with_retry(self, url, headers, data=None, json_data=None, timeout=15):
        import time
        max_retries = 3
        backoff = 1.0
        last_err = None
        for attempt in range(max_retries):
            try:
                if json_data is not None:
                    r = self.s.post(url, headers=headers, data=json.dumps(json_data), timeout=timeout)
                else:
                    r = self.s.post(url, headers=headers, data=data, timeout=timeout)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                last_err = e
                if attempt < max_retries - 1:
                    time.sleep(backoff * (2 ** attempt))
        raise FetchError(f"HTTP POST failed after {max_retries} attempts: {last_err}")

    def fetch_top10_by_trade_count(self, d):
        url = f"{self.BASE}/mostActiveTrades"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.cse.lk",
            "Referer": "https://www.cse.lk/pages/market-activity/market-activity.component.html"
        }

        data = self._post_with_retry(url, headers=headers, json_data={}, timeout=15)

        # take first 10 symbols as provided
        out = []
        for item in data:
            sym = item.get("symbol")
            if sym:
                out.append(sym)
        return out[:10]

    def fetch_daily_metrics(self, symbol, d):
        if not symbol:
            raise FetchError("Empty symbol")

        clean = symbol.replace(".N0000", "").strip().upper()
        api_symbols = [f"{clean}.N0000", clean]

        url = f"{self.BASE}/companyInfoSummery"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.cse.lk",
            "Referer": "https://www.cse.lk/"
        }

        def to_float(x, default=0.0):
            try:
                return float(x)
            except (TypeError, ValueError):
                return default

        last_err = None
        for api_symbol in api_symbols:
            try:
                data = self._post_with_retry(url, headers=headers, data={"symbol": api_symbol}, timeout=15)

                info = (data or {}).get("reqSymbolInfo")
                if not isinstance(info, dict):
                    continue

                # Confirmed keys from your browser payload
                return DailyMetrics(
                    turnover=to_float(info.get("tdyTurnover", 0.0)),
                    share_volume=to_float(info.get("tdyShareVolume", 0.0)),
                    trade_volume=to_float(info.get("tdyTradeVolume", 0.0)),
                    high=to_float(info.get("hiTrade", 0.0)),
                    low=to_float(info.get("lowTrade", 0.0)),
                    close=to_float(info.get("lastTradedPrice", 0.0)),
                    previous_close=to_float(info.get("previousClose", 0.0)),
                    change_percentage=to_float(info.get("changePercentage", 0.0)),
                )
            except Exception as e:
                last_err = e
                continue

        raise FetchError(f"companyInfoSummery failed for {symbol}: {last_err}")

    def fetch_static_metrics(self, symbol, d):
        clean = symbol.replace(".N0000", "").strip().upper()
        api_symbols = [f"{clean}.N0000", clean]

        url = f"{self.BASE}/companyInfoSummery"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.cse.lk",
            "Referer": "https://www.cse.lk/"
        }

        def to_float_or_none(x):
            try:
                return None if x is None else float(x)
            except (TypeError, ValueError):
                return None

        last_err = None
        for api_symbol in api_symbols:
            try:
                data = self._post_with_retry(url, headers=headers, data={"symbol": api_symbol}, timeout=15) or {}

                info = data.get("reqSymbolInfo") or {}
                beta = data.get("reqSymbolBetaInfo") or {}

                return StaticMetrics(
                    market_cap=float(info.get("marketCap", 0.0) or 0.0),
                    beta_aspi=to_float_or_none(beta.get("triASIBetaValue")),
                    beta_sl20=to_float_or_none(beta.get("betaValueSPSL")),
                )
            except Exception as e:
                last_err = e
                continue

        # Option B: static can be missing
        return StaticMetrics(market_cap=0.0, beta_aspi=None, beta_sl20=None)

    def fetch_top10_snapshot(self, d):
        url = f"{self.BASE}/mostActiveTrades"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.cse.lk",
            "Referer": "https://www.cse.lk/pages/market-activity/market-activity.component.html"
        }

        data = self._post_with_retry(url, headers=headers, json_data={}, timeout=15)

        # Build both: ordered top10 list + a metrics dict keyed by symbol
        top10 = []
        metrics = {}

        for item in data:
            sym = item.get("symbol")
            if not sym:
                continue

            if sym not in metrics:
                metrics[sym] = item  # store raw row so we can read turnover/tradeVolume etc.

            top10.append(sym)

        # remove duplicates, keep order
        seen = set()
        top10_unique = []
        for s in top10:
            if s not in seen:
                seen.add(s)
                top10_unique.append(s)

        top10_unique = top10_unique[:10]
        # keep only those in top10
        metrics = {s: metrics[s] for s in top10_unique if s in metrics}

        return top10_unique, metrics
