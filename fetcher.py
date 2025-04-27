
import requests
from config import COINGECKO_API_BASE, TOP_N_COINS, COINGECKO_API_KEY
from utils import log_resolution, print_progress_bar
import time

HEADERS = {"x-cg-pro-api-key": COINGECKO_API_KEY}

def get_top_gainers(period="1h"):
    url = f"{COINGECKO_API_BASE}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": TOP_N_COINS,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "1h"
    }
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    coins = response.json()

    if period == "1h":
        coins.sort(key=lambda x: x.get('price_change_percentage_1h_in_currency', 0), reverse=True)
    elif period == "4h":
        pass

    return [coin["id"] for coin in coins[:TOP_N_COINS]]

def get_ohlc_data_light(coin_id, vs_currency="usd", days="1"):
    url = f"{COINGECKO_API_BASE}/coins/{coin_id}/ohlc"
    params = {
        "vs_currency": vs_currency,
        "days": days
    }
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        ohlc_raw = response.json()

        formatted_data = []
        for entry in ohlc_raw:
            formatted_data.append({
                "timestamp": entry[0],
                "open": entry[1],
                "high": entry[2],
                "low": entry[3],
                "close": entry[4],
                "volume": None
            })
        return formatted_data

    except Exception as e:
        print(f"Error fetching LIGHT OHLC data for {coin_id}: {e}")
        return []

def get_ohlc_data_full(coin_id, vs_currency="usd", days="1", interval="hourly"):
    url = f"{COINGECKO_API_BASE}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": vs_currency,
        "days": days
    }
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        market_data = response.json()

        timestamps = [point[0] for point in market_data["prices"]]
        closes = [point[1] for point in market_data["prices"]]
        volumes = [point[1] for point in market_data["total_volumes"]]

        formatted_data = []
        for i in range(len(timestamps)):
            formatted_data.append({
                "timestamp": timestamps[i],
                "open": closes[i],
                "high": closes[i],
                "low": closes[i],
                "close": closes[i],
                "volume": volumes[i]
            })

        return formatted_data

    except Exception as e:
        print(f"Error fetching FULL OHLC data for {coin_id}: {e}")
        return []
