import pandas as pd
import streamlit as st
HEADERS = {"x-cg-pro-api-key": st.secrets["general"]["COINGECKO_API_KEY"]}

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
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    return [coin["id"] for coin in response.json()]

def get_ohlc_data(coin_id, days=1):
    try:
        url = f"{COINGECKO_API_BASE}/coins/{coin_id}/ohlc"
        params = {"vs_currency": "usd", "days": days}
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        log_resolution(coin_id, "Higher Accuracy (Hourly Data)", "Success")
        return response.json()
    except Exception as e:
        log_resolution(coin_id, "Higher Accuracy (Hourly Data)", f"Failed: {e}")
        # Placeholder: Add fallback to daily data here
        return []
def get_ohlc_data(coin_id, use_market_chart=False, vs_currency="usd", days="1"):
    if use_market_chart:
        url = f"{COINGECKO_API_BASE}/coins/{coin_id}/market_chart"
        params = {"vs_currency": vs_currency, "days": days}
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=5)
            response.raise_for_status()
            prices = response.json().get("prices", [])
            volumes = response.json().get("total_volumes", [])
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            df["volume"] = [v[1] for v in volumes]
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df["open"] = df["high"] = df["low"] = df["close"] = df["price"]
            return df[["timestamp", "open", "high", "low", "close", "volume"]]
        except:
            return pd.DataFrame()
    else:
        url = f"{COINGECKO_API_BASE}/coins/{coin_id}/ohlc"
        params = {"vs_currency": vs_currency, "days": days}
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=5)
            response.raise_for_status()
            ohlc = response.json()
            df = pd.DataFrame(ohlc, columns=["timestamp", "open", "high", "low", "close"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df
        except:
            return pd.DataFrame()
