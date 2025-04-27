
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from fetcher import get_top_gainers, get_ohlc_data_light, get_ohlc_data_full, get_btc_market_sentiment
from indicator_engine import IndicatorEngine
from utils import format_duration
from config import COINGECKO_API_KEY
import time

st.set_page_config(page_title="Crypto Dashboard v4.4", layout="wide")

st.title("🚀 Crypto Signal Dashboard (Top 10 True Gainers)")

# Auto-refresh every 120 seconds
st_autorefresh(interval=120000, key="market_sentiment_refresh")

# Sidebar
with st.sidebar:
    scan_mode = st.radio(
        "Choose Scanning Mode:",
        ("🛩️ Light Scan (Fast)", "🧠 Full Scan (Detailed)")
    )
    gainer_period = st.radio(
        "Top Gainers Period:",
        ("1h", "24h", "7d")
    )
    st.write(f"Using {scan_mode} mode scanning {gainer_period} gainers.")

# BTC Market Sentiment Gauge
btc_change = get_btc_market_sentiment()
if btc_change is not None:
    btc_change_clamped = max(-5.0, min(5.0, btc_change))
    gauge_value = (btc_change_clamped + 5) * (100 / 10)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=gauge_value,
        number={'suffix': "%"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "black", 'thickness': 0.3},
            'steps': [
                {'range': [0, 33], 'color': "red"},
                {'range': [33, 66], 'color': "yellow"},
                {'range': [66, 100], 'color': "green"}
            ],
        },
        title={'text': "Market Sentiment (BTC 1h % Change)"}
    ))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Unable to fetch BTC sentiment.")

# Fetch Top 10 Gainers
top_coins = get_top_gainers(period=gainer_period)

if not top_coins:
    st.error("⚠️ Failed to fetch top coins. Please wait and try again.")
    st.stop()

# Display results
st.subheader(f"Top 10 Gainers ({gainer_period})")

for coin_id in top_coins:
    if "Light" in scan_mode:
        ohlc_data = get_ohlc_data_light(coin_id)
    else:
        ohlc_data = get_ohlc_data_full(coin_id)

    if not ohlc_data:
        st.warning(f"⚠️ No OHLC data for {coin_id}. Skipping.")
        continue

    df = pd.DataFrame(ohlc_data)
    engine = IndicatorEngine(df)
    engine.run_all_indicators()
    scores = engine.generate_score(debug=True)
    signal = engine.generate_signal()

    with st.container():
        st.subheader(f"🪙 {coin_id.capitalize()}")
        st.write(f"Total Score: {scores['total_score']:.2f}")
        st.write(f"Signal: {signal['signal']}")
        st.write(f"Reason: {signal['reason']}")
