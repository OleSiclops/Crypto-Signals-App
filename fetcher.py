
import requests
from config import COINGECKO_API_BASE, TOP_N_COINS, COINGECKO_API_KEY

HEADERS = {"x-cg-pro-api-key": COINGECKO_API_KEY}

def get_top_gainers(period="1h"):
    url = f"{COINGECKO_API_BASE}/coins/markets"
    if period == "1h":
        order_param = "price_change_percentage_1h_desc"
    elif period == "24h":
        order_param = "price_change_percentage_24h_desc"
    else:
        order_param = "market_cap_desc"

    params = {
        "vs_currency": "usd",
        "order": order_param,
        "per_page": TOP_N_COINS,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "1h,24h"
    }
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    coins = response.json()
    return [coin["id"] for coin in coins[:TOP_N_COINS]]

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

def get_ohlc_data_full(coin_id, vs_currency="usd", days="1"):
    url = f"{COINGECKO_API_BASE}/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days}
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        market_data = response.json()
        timestamps = [point[0] for point in market_data["prices"]]
        closes = [point[1] for point in market_data["prices"]]
        volumes = [point[1] for point in market_data["total_volumes"]]
        return [{
            "timestamp": timestamps[i],
            "open": closes[i],
            "high": closes[i],
            "low": closes[i],
            "close": closes[i],
            "volume": volumes[i]
        } for i in range(len(timestamps))]
    except Exception as e:
        print(f"Error fetching FULL OHLC: {e}")
        return []

def get_btc_market_sentiment():
    url = f"{COINGECKO_API_BASE}/coins/bitcoin"
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false"
    }
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        btc_change_1h = data['market_data']['price_change_percentage_1h_in_currency']['usd']
        return btc_change_1h
    except Exception as e:
        print(f"Error fetching BTC market sentiment: {e}")
        return None
