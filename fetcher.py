
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
    
    # DIAGNOSTIC: Print API key info and headers
    print(f"DIAGNOSTIC: API Key Length: {len(COINGECKO_API_KEY)}")
    print(f"DIAGNOSTIC: API Key Start: {COINGECKO_API_KEY[:6]}...")
    print(f"DIAGNOSTIC: Headers being sent: {HEADERS}")
    
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        print(f"DIAGNOSTIC: Response Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"DIAGNOSTIC: Response Text: {response.text}")

        response.raise_for_status()
        coins = response.json()
        return [coin["id"] for coin in coins[:TOP_N_COINS]]
    except Exception as e:
        print(f"Error fetching top gainers: {e}")
        return []
