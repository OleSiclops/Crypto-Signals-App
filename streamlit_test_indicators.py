
import streamlit as st
st.write("🔍 TOP OF FILE LOADED")
st.write("🔍 TOP OF FILE LOADED")
import pandas as pd
import plotly.graph_objects as go
import requests
import random
import ta
from streamlit_autorefresh import st_autorefresh
from indicator_engine_v2 import IndicatorEngineV2

COINGECKO_API_BASE = "https://pro-api.coingecko.com/api/v3"
TOP_N_COINS = 50
HEADERS = {"x-cg-pro-api-key": st.secrets["general"]["COINGECKO_API_KEY"]}

def fetch_btc_24h_prices():
    url = f"{COINGECKO_API_BASE}/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "1"}
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=5)
        response.raise_for_status()
        data = response.json().get("prices", [])
        df = pd.DataFrame(data, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception as e:
        st.warning("⚠️ Failed to fetch BTC 24h prices. Skipping chart...")
        return pd.DataFrame()

def get_btc_market_sentiment():
    url = f"{COINGECKO_API_BASE}/coins/bitcoin"
    params = {"localization": "false", "tickers": "false", "market_data": "true"}
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data['market_data']['price_change_percentage_1h_in_currency']['usd']
    except:
        st.warning("⚠️ Failed to fetch BTC sentiment. Showing neutral gauge.")
        return 0.0

def plot_btc_chart(df):
    if df.empty:
        st.warning("No BTC price data to display.")
        return
    df.set_index("timestamp", inplace=True)
    df["SMA_12h"] = df["price"].rolling(window=12).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["price"], mode="lines", name="BTC Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA_12h"], mode="lines", name="12h SMA", line=dict(dash="dot")))
    fig.update_layout(title="BTC 24h Price Chart with 12h SMA", height=350)
    st.plotly_chart(fig, use_container_width=True, key="btc_chart")

st.write("✅ App reached end of script")
st.markdown("**✅ Streamlit is rendering this app correctly.**")
