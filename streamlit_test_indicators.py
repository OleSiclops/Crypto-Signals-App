
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from fetcher import get_top_gainers
from config import COINGECKO_API_KEY
import time

st.set_page_config(page_title="Crypto Diagnostic Visible", layout="wide")

st.title("🚀 Crypto Signal Dashboard (Visible Diagnostics)")

# Auto-refresh every 120 seconds
st_autorefresh(interval=120000, key="market_sentiment_refresh")

# Fetch coins and diagnostic info
top_coins, diagnostics = get_top_gainers()

with st.sidebar:
    st.subheader("Diagnostics")
    st.write(f"API Key Length: {diagnostics.get('api_key_length')}")
    st.write(f"API Key Start: {diagnostics.get('api_key_start')}")
    st.write(f"Headers Sent: {diagnostics.get('headers_sent')}")

st.subheader("Fetch Result")

if "error" in diagnostics:
    st.error(f"Error fetching coins: {diagnostics['error']}")
elif not top_coins:
    st.warning("⚠️ No coins fetched. Maybe CoinGecko rejected?")
else:
    st.success(f"First Top Coin ID: {diagnostics.get('first_coin_id', 'Unknown')}")

st.subheader("HTTP Response Info")
st.write(f"Response Status Code: {diagnostics.get('response_status_code', 'Unknown')}")
if "response_body" in diagnostics:
    st.code(diagnostics["response_body"])
