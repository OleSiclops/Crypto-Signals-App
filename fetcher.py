# fetcher.py

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
    }
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    coins = response.json()

    if period == "1h":
        coins.sort(key=lambda x: x.get('price_change_percentage_1h_in_currency', 0), reverse=True)
    elif period == "4h":
        pass

    return [coin["id"] for coin in coins[:TOP_N_COINS]]
