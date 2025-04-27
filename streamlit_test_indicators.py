
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.graph_objects as go
from indicator_engine import IndicatorEngine
from fetcher import get_top_gainers, get_ohlc_data_light, get_ohlc_data_full
from utils import format_duration
from config import COINGECKO_API_KEY
import time

st.set_page_config(page_title="Crypto Signal Dashboard", layout="wide")

# Debug: Show API Key info in sidebar
st.sidebar.success(f"API Key Preview: {COINGECKO_API_KEY[:6]}... (length: {len(COINGECKO_API_KEY)})")

# Auto-refresh every 60 seconds
st_autorefresh(interval=60000, key="market_sentiment_refresh")

st.title("🚀 Crypto Technical Scorecards + Signal Detector (v4.0 Real OHLC)")

# Sidebar toggle
with st.sidebar:
    scan_mode = st.radio(
        "Choose Scanning Mode:",
        ("🛩️ Light Scan (Fast)", "🧠 Full Scan (Detailed)")
    )

    if "Light" in scan_mode:
        st.markdown("""
            ⚡ **Light Scan:**  
            - Ultra-fast scanning  
            - Price-based indicators only  
            - No volume analysis
        """)
    else:
        st.markdown("""
            🧠 **Full Scan:**  
            - Includes volume-based indicators (VWAP, Volume Change)  
            - More accurate signals  
            - Slightly slower scan
        """)

# Get top coin
top_coins = get_top_gainers()
if "Light" in scan_mode:
    ohlc_data = get_ohlc_data_light(top_coins[0])
else:
    ohlc_data = get_ohlc_data_full(top_coins[0])

# Dataframe
df = pd.DataFrame(ohlc_data)

# Indicator Analysis
engine = IndicatorEngine(df)
engine.run_all_indicators()
scores = engine.generate_score(debug=True)
signal_output = engine.generate_signal()

# Display
with st.container():
    st.markdown("## 🪙 Sample Coin Analysis")
    st.markdown(f"### 🏆 **Total Score:** {scores['total_score']:.2f}")
    st.markdown(f"### 📈 **Signal:** {signal_output['signal']}")
    st.markdown(f"### 📋 **Reason:** {signal_output['reason']}")
