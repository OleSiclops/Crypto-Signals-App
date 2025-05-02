API_KEY = st.secrets["api"]["coingecko_key"]
import streamlit as st

# fetcher.py

import requests
from config import COINGECKO_API_BASE, TOP_N_COINS
from utils import log_resolution

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

def get_ohlc_data(coin_id, days=1):
    try:
        url = f"{COINGECKO_API_BASE}/coins/{coin_id}/ohlc"
        params = {"vs_currency": "usd", "days": days}
        response = requests.get(url, params=params)
        response.raise_for_status()
        log_resolution(coin_id, "Higher Accuracy (Hourly Data)", "Success")
        return response.json()
    except Exception as e:
        log_resolution(coin_id, "Higher Accuracy (Hourly Data)", f"Failed: {e}")
        # Placeholder: Add fallback to daily data here
        return []
