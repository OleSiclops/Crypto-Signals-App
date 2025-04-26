import requests
from config import COINGECKO_API_BASE, TOP_N_COINS
from utils import log_resolution, print_progress_bar
import time

TOP_25_TAGS = [
    "real-world-assets", "depin", "defi", "smart-contract-platform", "layer-2", "stablecoin",
    "nft", "artificial-intelligence", "gaming", "metaverse", "oracles", "yield-farming",
    "liquidity-mining", "dex", "privacy-coin", "infrastructure", "decentralized-storage",
    "meme-token", "dao", "launchpad", "cross-chain", "identity", "staking", "payments", "web3"
]

def get_top_gainers(period="1h"):
    url = f"{COINGECKO_API_BASE}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "percent_change_1h_desc" if period == "1h" else "percent_change_4h_desc",
        "per_page": TOP_N_COINS,
        "page": 1,
        "price_change_percentage": "1h,4h"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return [coin["id"] for coin in response.json()]

def get_coin_metadata(coin_id):
    try:
        url = f"{COINGECKO_API_BASE}/coins/{coin_id}"
        params = {"localization": "false"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        categories = data.get("categories", [])
        tags = data.get("tags", [])

        main_category = "Uncategorized"
        if categories:
            if "DeFi" in categories:
                main_category = "DeFi"
            elif "NFT" in categories:
                main_category = "NFT"
            elif any(cat for cat in categories if "Layer 1" in cat or "Smart Contract" in cat):
                main_category = "Layer 1"
            elif "Meme" in categories:
                main_category = "Meme"

        special_tags = []
        for tag in tags:
            if tag in TOP_25_TAGS:
                special_tags.append(tag.replace("-", " ").title())
        
        if not special_tags:
            special_tags = ["Not in Top 25"]
        
        return {
            "id": coin_id,
            "name": data.get("name"),
            "symbol": data.get("symbol"),
            "logo": data.get("image", {}).get("thumb"),
            "categories": categories,
            "tags": tags,
            "main_category": main_category,
            "special_tags": special_tags,
            "homepage": data.get("links", {}).get("homepage", [""])[0]
        }
    except Exception as e:
        log_resolution(coin_id, "Metadata Fetch", f"Failed: {e}")
        return {}

def get_ohlc_data(coin_id, days=1, retries=1):
    attempt = 0
    while attempt <= retries:
        try:
            url = f"{COINGECKO_API_BASE}/coins/{coin_id}/ohlc"
            params = {"vs_currency": "usd", "days": days}
            response = requests.get(url, params=params)
            response.raise_for_status()
            log_resolution(coin_id, "Higher Accuracy (Hourly Data)", "Success")
            return response.json()
        except Exception as e:
            log_resolution(coin_id, "Higher Accuracy (Hourly Data)", f"Failed (Attempt {attempt+1}): {e}")
            attempt += 1
            time.sleep(1)
    
    try:
        fallback_url = f"{COINGECKO_API_BASE}/coins/{coin_id}/ohlc"
        fallback_params = {"vs_currency": "usd", "days": 7}
        fallback_response = requests.get(fallback_url, params=fallback_params)
        fallback_response.raise_for_status()
        log_resolution(coin_id, "Lower Accuracy (Daily Data)", "Success (Fallback)")
        return fallback_response.json()
    except Exception as fallback_e:
        log_resolution(coin_id, "Lower Accuracy (Daily Data)", f"Failed: {fallback_e}")
        return []

def fetch_multiple_enriched_coins(coin_ids, days=1):
    all_data = {}
    print_progress_bar(0, len(coin_ids), prefix='Progress:', suffix='Complete', length=50)
    for idx, coin_id in enumerate(coin_ids):
        metadata = get_coin_metadata(coin_id)
        ohlc = get_ohlc_data(coin_id, days=days)
        all_data[coin_id] = {
            "metadata": metadata,
            "ohlc": ohlc
        }
        print_progress_bar(idx + 1, len(coin_ids), prefix='Progress:', suffix='Complete', length=50)
    return all_data
