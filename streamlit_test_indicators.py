
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from indicator_engine_v2 import IndicatorEngineV2

st.write("🔍 TOP OF FILE LOADED")

def fetch_btc_24h_prices():
    url = "https://pro-api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "1"}
    params["x_cg_pro_api_key"] = st.secrets["general"]["COINGECKO_API_KEY"]
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json().get("prices", [])
        df = pd.DataFrame(data, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception as e:
        st.warning("⚠️ Failed to fetch BTC 24h prices.")
        return pd.DataFrame()

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

# Step 1: BTC Chart
st.write("🔁 Step 1: Fetching BTC price data")
btc_df = fetch_btc_24h_prices()
st.write("📊 BTC Data Head:", btc_df.head())
plot_btc_chart(btc_df)

# Step 2: Sidebar Controls
with st.sidebar:
    st.write("🧭 **Scan Configuration**")
    scan_mode = st.radio("Scan Mode", options=["Light", "Full"], index=0)
    period = st.selectbox("Top Gainers Period", options=["1h", "4h", "24h", "7d"], index=0)
    st.write("📌 Selected Mode:", scan_mode)
    st.write("⏱ Scan Period:", period)

# Step 3: Market Indicator at a Glance
with st.expander("📊 Market Indicator at a Glance", expanded=True):
    st.markdown("""
    <div style='background-color: #e0e0e0; padding: 10px; border-radius: 8px;'>
    """, unsafe_allow_html=True)

    st.write("🔧 Calculating market indicators...")
    btc_indicators = IndicatorEngineV2(btc_df).calculate_all() if not btc_df.empty else {}

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("BTC 1h Change", f"{btc_df['price'].pct_change().iloc[-1] * 100:.2f}%" if not btc_df.empty else "N/A")
        rsi_val = btc_indicators.get("RSI", "N/A")
        st.metric("RSI", rsi_val)

    with col2:
        macd_val = btc_indicators.get("MACD", "N/A")
        st.metric("MACD", "Bullish" if macd_val == 100 else "Bearish" if macd_val == 30 else "Neutral")
        ema_val = btc_indicators.get("EMA", "N/A")
        st.metric("EMA Trend", "Above 50 EMA" if ema_val == 100 else "Below 50 EMA" if ema_val == 30 else "N/A")

    with col3:
        volume_val = btc_indicators.get("Volume", "N/A")
        st.metric("Volume", "High" if volume_val == 100 else "Moderate" if volume_val == 60 else "Low" if volume_val == 30 else "N/A")

        try:
            fng_response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5).json()
            fng_value = fng_response["data"][0]["value"]
            fng_classification = fng_response["data"][0]["value_classification"]
            st.metric("Fear & Greed", f"{fng_value} ({fng_classification})")
        except:
            st.metric("Fear & Greed", "N/A")

    st.markdown("</div>", unsafe_allow_html=True)

st.write("✅ End of Step 3")
