
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from fetcher import get_top_gainers, get_ohlc_data_light
from indicator_engine import IndicatorEngine
from utils import format_duration
from config import COINGECKO_API_KEY
import time

st.set_page_config(page_title="Crypto Dashboard", layout="wide")

# Debug - Show API Key Length
st.sidebar.success(f"API Key Length: {len(COINGECKO_API_KEY)}")

# Auto-refresh
st_autorefresh(interval=60000, key="market_sentiment_refresh")

st.title("🚀 Crypto Signal Dashboard")

top_coins = get_top_gainers()
ohlc_data = get_ohlc_data_light(top_coins[0])
df = pd.DataFrame(ohlc_data)

engine = IndicatorEngine(df)
engine.run_all_indicators()
scores = engine.generate_score(debug=True)
signal = engine.generate_signal()

with st.container():
    st.subheader(f"Sample Coin: {top_coins[0]}")
    st.write(f"Total Score: {scores['total_score']:.2f}")
    st.write(f"Signal: {signal['signal']}")
    st.write(f"Reason: {signal['reason']}")
