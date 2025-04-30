
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from indicator_engine_v2 import IndicatorEngineV2

def get_category_label(score):
    if score >= 80:
        return "Exceptional Gains 🚀"
    elif score >= 65:
        return "Moderate Gains 👍"
    elif score >= 50:
        return "Modest Gains 🟡"
    return "Low Confidence"

def generate_reason(symbol, indicators):
    parts = []
    if indicators.get("RSI", 0) >= 70:
        parts.append("RSI indicates strong momentum")
    if indicators.get("MACD", 0) >= 60:
        parts.append("MACD shows bullish crossover")
    if indicators.get("EMA", 0) >= 60:
        parts.append("Price trending above EMA")
    if indicators.get("Volume", 0) >= 70:
        parts.append("Volume surge confirms buying pressure")
    return " and ".join(parts) + f" on {symbol}"

def display_signal_card(sig):
    buy_score = sig["buy_score"]
    category = get_category_label(buy_score)
    reason = generate_reason(sig["symbol"], sig["indicators"])
    entry = sig["recommended_entry"]
    gain_pct = sig["estimated_gain_pct"]
    projected_exit = entry * (1 + gain_pct / 100)

    st.markdown(f"""
    <div style='border: 1px solid #ccc; border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem;'>
      <div style='height: 8px; border-radius: 4px; background: linear-gradient(90deg, #4caf50 {buy_score}%, #ccc {buy_score}%);'></div>
      <h4 style='margin-top: 10px;'>🪙 {sig["name"]} ({sig["symbol"]})</h4>
      <p><strong>💰 Buy Score:</strong> {buy_score} — <em>{category}</em></p>
      <p><strong>🎯 Entry Range:</strong> ${entry * 0.99:.2f} – ${entry * 1.01:.2f}</p>
      <p><strong>📈 Est. Gain:</strong> {gain_pct:.1f}% → <strong>Target:</strong> ${projected_exit:.2f}</p>
      <p><strong>🧠 Reason:</strong> {reason}</p>
      <small>Indicators: {" | ".join([f"{k}: {v}" for k,v in sig["indicators"].items()])}</small>
    </div>
    """, unsafe_allow_html=True)


st.set_page_config(page_title="Crypto Signal Dashboard v4.6.0", layout="wide")
st.title("🚀 Crypto Signal Dashboard v4.6.0 – Humanized Analysis")

def fetch_mock_signal_data():
    return [
        {
            "symbol": "ETH",
            "name": "Ethereum",
            "buy_score": 84,
            "recommended_entry": 3145.23,
            "estimated_gain_pct": 12.4,
            "indicators": {"RSI": 75, "MACD": 80, "EMA": 100, "Volume": 60}
        },
        {
            "symbol": "SOL",
            "name": "Solana",
            "buy_score": 67,
            "recommended_entry": 142.78,
            "estimated_gain_pct": 6.3,
            "indicators": {"RSI": 65, "MACD": 60, "EMA": 70, "Volume": 100}
        }
    ]

st.subheader("📊 Buy Signals")
signals = fetch_mock_signal_data()
cols = st.columns(2)

for i, sig in enumerate(signals):
    if sig["buy_score"] >= 50:
        with cols[i % 2]:
            display_signal_card(sig)
