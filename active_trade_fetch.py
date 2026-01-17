import requests
import datetime
import requests
import json


def get_stock_price(symbol):
    if not symbol:
        return None

    # Clean the symbol: remove suffix, trim whitespace, and uppercase
    clean_symbol = symbol.replace(".N0000", "").strip().upper()

    # List of symbols to try (matches the JS logic)
    api_symbols = [f"{clean_symbol}.N0000", clean_symbol]

    for api_symbol in api_symbols:
        # Define the form data (payload)
        payload = {'symbol': api_symbol}

        # Define headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            # Construct the full URL
            url = f"https://www.cse.lk/api/companyInfoSummery"

            # Make the POST request
            response = requests.post(url, data=payload, headers=headers, timeout=10)

            # Check if request was successful
            if response.status_code == 200:
                data = response.json()

                # Check for the specific data structure
                if data and "reqSymbolInfo" in data:
                    price_str = data["reqSymbolInfo"].get("lastTradedPrice")
                    try:
                        return float(price_str)
                    except (ValueError, TypeError):
                        return 0.0

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {api_symbol}: {e}")

    return None



def fetch_cse_top_trades():
    # The endpoint used by the CSE web portal for most active trades
    url = "https://www.cse.lk/api/mostActiveTrades"

    # Headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.cse.lk",
        "Referer": "https://www.cse.lk/pages/market-activity/market-activity.component.html"
    }

    # Usually, these endpoints require an empty JSON object or specific parameters
    payload = {}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            data = response.json()
            print(f"{'Symbol':<10} | {'Volume':<12} | {'Price(LKR)':<10} |{'Turnover (LKR)':<15}")
            print("-" * 45)

            # Extracting and printing the trades (structure might vary slightly based on current API version)
            active_data = []
            for trade in data:
                symbol = trade.get('symbol', 'N/A')
                volume = trade.get('tradeVolume', 0)
                price = get_stock_price(symbol)
                turnover = trade.get('turnover', 0)

                active_data.append(
                    {
                        "symbol": symbol,
                        "volume": volume,
                        "turnover": turnover,
                        "price": price
                    }
                )
                write_top_trade_data(active_data)
                print(f"{symbol:<10} | {volume:<12,} | {price:<10} |{turnover:<15,.2f}")
        else:
            print(f"Failed to fetch data. Status Code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")

def write_top_trade_data(active_data):
        today = datetime.date.today().isoformat()
        with open(f"{today}.json", "w") as f:
            json.dump(active_data, f, indent=2)


if __name__ == "__main__":
    fetch_cse_top_trades()


