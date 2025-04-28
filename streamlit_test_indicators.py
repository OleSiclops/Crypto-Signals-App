
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import requests

COINGECKO_API_BASE = "https://pro-api.coingecko.com/api/v3"
TOP_N_COINS = 300
HEADERS = {"x-cg-pro-api-key": st.secrets["general"]["COINGECKO_API_KEY"]}

def get_top_gainers(period="1h"):
    url = f"{COINGECKO_API_BASE}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": TOP_N_COINS,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "1h,24h,7d"
    }
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    coins = response.json()

    if period == "1h":
        key = "price_change_percentage_1h_in_currency"
    elif period == "24h":
        key = "price_change_percentage_24h_in_currency"
    elif period == "7d":
        key = "price_change_percentage_7d_in_currency"
    else:
        key = "price_change_percentage_24h_in_currency"

    coins_sorted = sorted(
        coins,
        key=lambda x: x.get(key, 0) or 0,
        reverse=True
    )

    return [coin["id"] for coin in coins_sorted[:TOP_N_COINS]]

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
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return data['market_data']['price_change_percentage_1h_in_currency']['usd']

st.set_page_config(page_title="Crypto Dashboard v4.5", layout="wide")
st.title("🚀 Crypto Signal Dashboard (Strong Buy Cards)")
st_autorefresh(interval=120000, key="market_sentiment_refresh")

with st.sidebar:
    scan_mode = st.radio("Choose Scanning Mode:", ("🛩️ Light Scan (Fast)", "🧠 Full Scan (Detailed)"))
    gainer_period = st.radio("Top Gainers Period:", ("1h", "24h", "7d"))

btc_change = get_btc_market_sentiment()
btc_change_clamped = max(-5.0, min(5.0, btc_change))
gauge_value = (btc_change_clamped + 5) * (100 / 10)
fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=gauge_value,
    number={'suffix': "%"},
    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "black", 'thickness': 0.3},
           'steps': [{'range': [0, 33], 'color': "red"},
                     {'range': [33, 66], 'color': "yellow"},
                     {'range': [66, 100], 'color': "green"}]},
    title={'text': "Market Sentiment (BTC 1h % Change)"}
))
st.plotly_chart(fig, use_container_width=True)

top_coins = get_top_gainers(period=gainer_period)

if not top_coins:
    st.error("⚠️ Failed to fetch top coins. Please wait and try again.")
    st.stop()

# Dummy placeholder: here you'd normally scan with IndicatorEngine, etc.
# I'll skip scanning for dummy strong BUYs here to demonstrate layout.

# For now, simulate 5 example strong BUYs:
example_buys = [
    ("Bitcoin", 85.3, "Strong bullish technicals."),
    ("Ethereum", 82.1, "Strong bullish technicals."),
    ("Solana", 78.7, "Strong bullish technicals."),
    ("Ripple", 76.4, "Strong bullish technicals."),
    ("Dogecoin", 74.9, "Strong bullish technicals.")
]

buy_signals = example_buys

if not buy_signals:
    st.warning("⚠️ No strong BUY signals detected at this time.")
else:
    st.subheader(f"Top {min(20, len(buy_signals))} Strong BUY Signals ({gainer_period})")

    cols = st.columns(3)
    for idx, (coin_id, score, reason) in enumerate(buy_signals[:20]):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"### 🪙 {coin_id}")
                st.metric(label="Total Score", value=f"{score:.2f}")
                st.success(f"✅ {reason}")
