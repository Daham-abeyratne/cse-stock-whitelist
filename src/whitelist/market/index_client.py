import requests
import json
from typing import Dict
from ..util.errors import FetchError

class IndexClient:
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

    def fetch_index_summary(self, d) -> Dict[str, float]:
        url = f"{self.BASE}/marketSummary"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.cse.lk"
        }
        data = self._post_with_retry(url, headers=headers, json_data={}, timeout=15)
        
        out = {"ASPI": 0.0, "S&P SL20": 0.0}
        
        # Typically the indices might be under a different key or array
        # This acts as a best-effort parse based on typical CSE structure
        if isinstance(data, dict) and "reqMarketSummary" in data:
            for item in data["reqMarketSummary"]:
                name = item.get("indexName")
                if name in out:
                    out[name] = float(item.get("currentValue", 0.0))
        elif isinstance(data, list):
            for item in data:
                name = item.get("indexName")
                if name in out:
                    out[name] = float(item.get("currentValue", 0.0))
                    
        return out
