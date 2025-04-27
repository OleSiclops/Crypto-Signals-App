
import requests
from config import COINGECKO_API_BASE, TOP_N_COINS, COINGECKO_API_KEY

HEADERS = {"x-cg-pro-api-key": COINGECKO_API_KEY}

def get_top_gainers():
    url = f"{COINGECKO_API_BASE}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": TOP_N_COINS,
        "page": 1,
        "sparkline": "false"
    }
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        coins = response.json()
        return [coin["id"] for coin in coins[:TOP_N_COINS]]
    except Exception as e:
        print(f"Error fetching top gainers: {e}")
        return []
    
def get_ohlc_data_light(coin_id, vs_currency="usd", days="1"):
    url = f"{COINGECKO_API_BASE}/coins/{coin_id}/ohlc"
    params = {"vs_currency": vs_currency, "days": days}
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        ohlc_raw = response.json()
        return [{
            "timestamp": entry[0],
            "open": entry[1],
            "high": entry[2],
            "low": entry[3],
            "close": entry[4],
            "volume": None
        } for entry in ohlc_raw]
    except Exception as e:
        print(f"Error fetching OHLC: {e}")
        return []
