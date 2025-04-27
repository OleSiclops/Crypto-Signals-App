# streamlit_test_indicators.py

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.graph_objects as go
from indicator_engine import IndicatorEngine
from fetcher import get_btc_market_sentiment
from utils import format_duration
import time

st.set_page_config(page_title="Crypto Signal Dashboard", layout="wide")

# Auto-refresh every 60 seconds
st_autorefresh(interval=60000, key="market_sentiment_refresh")

st.title("🚀 Crypto Technical Scorecards + Signal Detector (v3.3 Fine-Scale Gauge)")

# Session state setup
if "launch_time" not in st.session_state:
    st.session_state.launch_time = time.time()
if "last_sentiment" not in st.session_state:
    st.session_state.last_sentiment = None
if "last_sentiment_change_time" not in st.session_state:
    st.session_state.last_sentiment_change_time = time.time()

# Fetch sentiment
sentiment, btc_change = get_btc_market_sentiment()

# Detect sentiment change
if st.session_state.last_sentiment != sentiment:
    st.session_state.last_sentiment = sentiment
    st.session_state.last_sentiment_change_time = time.time()

# Calculate duration since last sentiment change
elapsed_seconds = time.time() - st.session_state.last_sentiment_change_time
elapsed_time_str = format_duration(elapsed_seconds)

# Display market status text
st.markdown(f"### 🌎 Market Status: **{sentiment} ({btc_change:+.2f}%)** — {elapsed_time_str}")

# Fine-scale gauge mapping
# BTC 1h change from -5% to +5% maps to 0-100 gauge
btc_change_clamped = max(-5.0, min(5.0, btc_change))
gauge_value = (btc_change_clamped + 5) * (100 / 10)
gauge_color = {"Bullish": "green", "Consolidating": "yellow", "Bearish": "red"}.get(sentiment, "yellow")

fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=gauge_value,
    number={'suffix': "%"},
    gauge={
        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
        'bar': {'color': "black", 'thickness': 0.3},
        'bgcolor': "white",
        'steps': [
            {'range': [0, 33], 'color': "red"},
            {'range': [33, 66], 'color': "yellow"},
            {'range': [66, 100], 'color': "green"}
        ],
        'threshold': {
            'line': {'color': gauge_color, 'width': 6},
            'thickness': 0.8,
            'value': gauge_value
        }
    },
    title={'text': "Market Sentiment Gauge (Fine Scale)"}
))

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Dummy OHLC data
sample_data = {
    "timestamp": pd.date_range(end=pd.Timestamp.now(), periods=50, freq="H").astype(int) / 10**6,
    "open": [100 + i*0.5 for i in range(50)],
    "high": [101 + i*0.5 for i in range(50)],
    "low": [99 + i*0.5 for i in range(50)],
    "close": [100 + i*0.5 + (i % 5) for i in range(50)],
    "volume": [1000 + i*10 for i in range(50)]
}

df = pd.DataFrame(sample_data)

engine = IndicatorEngine(df)
engine.run_all_indicators()
latest_signals = engine.get_latest_indicators()
scores = engine.generate_score(debug=True)
signal_output = engine.generate_signal()

with st.container():
    st.markdown("## 🪙 Sample Coin")
    st.markdown(f"### 🏆 **Total Score:** {scores['total_score']:.2f}")
    st.markdown(f"### 📈 **Signal:** {signal_output['signal']}")
    st.markdown(f"### 📋 **Reason:** {signal_output['reason']}")
    st.markdown("### 📊 Indicator Scores:")
    st.markdown(f"- **RSI Score:** {scores.get('rsi_score', 0):.2f}")
    st.markdown(f"- **StochRSI Score:** {scores.get('stoch_rsi_score', 0):.2f}")
    st.markdown(f"- **EMA Crossover Score:** {scores.get('ema_crossover_score', 0):.2f}")
    st.markdown(f"- **BB Width Score:** {scores.get('bb_width_score', 0):.2f}")
    st.markdown(f"- **Volume Change Score:** {scores.get('volume_change_score', 0):.2f}")
    st.markdown(f"- **VWAP Bias Score:** {scores.get('vwap_bias_score', 0):.2f}")
    st.markdown("---")
