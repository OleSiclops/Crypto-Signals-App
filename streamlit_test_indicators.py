
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from fetcher import get_top_gainers
from indicator_engine import IndicatorEngine
from config import COINGECKO_API_KEY
import time

st.set_page_config(page_title="Crypto Diagnostic", layout="wide")

# Debug - Show API Key Length
st.sidebar.success(f"API Key Length: {len(COINGECKO_API_KEY)}")

# Auto-refresh every 120 seconds
st_autorefresh(interval=120000, key="market_sentiment_refresh")

st.title("🚀 Crypto Signal Dashboard (Diagnostic Mode)")

top_coins = get_top_gainers()

if not top_coins:
    st.error("⚠️ Failed to fetch top coins. Please wait and try again.")
    st.stop()

st.write(f"Fetched Top Coin: {top_coins[0]}")
