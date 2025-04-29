
# Hotfixed Streamlit app v4.5.4 (with 5-second timeout and safe fallbacks)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import random
import ta
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

COINGECKO_API_BASE = "https://pro-api.coingecko.com/api/v3"
TOP_N_COINS = 300
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
        st.warning(f"⚠️ Failed to fetch BTC 24h prices. Skipping chart...")
        return pd.DataFrame()

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
        response = requests.get(url, params=params, headers=HEADERS, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data['market_data']['price_change_percentage_1h_in_currency']['usd']
    except Exception as e:
        st.warning(f"⚠️ Failed to fetch BTC sentiment. Showing neutral gauge.")
        return 0.0

def plot_btc_24h_chart(df_prices):
    if df_prices.empty:
        st.warning("No BTC price data to display.")
        return

    df_prices.set_index("timestamp", inplace=True)
    df_prices["SMA_12h"] = df_prices["price"].rolling(window=12).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_prices.index, y=df_prices["price"], mode="lines", name="BTC Price"))
    fig.add_trace(go.Scatter(x=df_prices.index, y=df_prices["SMA_12h"], mode="lines", name="12h SMA", line=dict(dash="dot")))

    fig.update_layout(title="BTC 24h Price Chart with 12h SMA",
                      xaxis_title="Time",
                      yaxis_title="Price (USD)",
                      height=350,
                      margin=dict(l=20, r=20, t=40, b=20))

    st.plotly_chart(fig, use_container_width=True)

st.set_page_config(page_title="Crypto Dashboard v4.5.4 Hotfix1", layout="wide")

st.title("🚀 Crypto Signal Dashboard v4.5.4 Hotfix1 – with BTC Chart and Timeouts")
st_autorefresh(interval=120000, key="market_sentiment_refresh")

# New Layout: BTC Chart and Sentiment Gauge Side by Side
col1, col2 = st.columns([2, 1])

with col1:
    btc_prices_df = fetch_btc_24h_prices()
    plot_btc_24h_chart(btc_prices_df)

with col2:
    btc_change = get_btc_market_sentiment()
    btc_change_clamped = max(-5.0, min(5.0, btc_change))
    gauge_value = (btc_change_clamped + 5) * (100 / 10)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=gauge_value,
        number={'suffix': "%"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "black", 'thickness': 0.3},
               'steps': [{'range': [0, 33], 'color': "red"},
                         {'range': [33, 66], 'color': "yellow"},
                         {'range': [66, 100], 'color': "green"}]},
        title={'text': "Market Sentiment (BTC 1h % Change)"}
    ))
    st.plotly_chart(fig, use_container_width=True)

# Signal Scanner Logic Continues Here (Gainers, Signal Cards, etc.)
