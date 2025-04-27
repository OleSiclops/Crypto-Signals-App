
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
    
    diagnostics = {}
    diagnostics["api_key_length"] = len(COINGECKO_API_KEY)
    diagnostics["api_key_start"] = COINGECKO_API_KEY[:6]
    diagnostics["headers_sent"] = str(HEADERS)

    try:
        response = requests.get(url, params=params, headers=HEADERS)
        diagnostics["response_status_code"] = response.status_code
        
        if response.status_code != 200:
            diagnostics["response_body"] = response.text

        response.raise_for_status()
        coins = response.json()
        diagnostics["first_coin_id"] = coins[0]["id"] if coins else "No coins returned"
        return coins, diagnostics
    except Exception as e:
        diagnostics["error"] = str(e)
        return [], diagnostics
