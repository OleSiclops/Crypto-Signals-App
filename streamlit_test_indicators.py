
import streamlit as st
from display_signal_card import display_signal_card

st.set_page_config(page_title="Crypto Signal Dashboard v4.6.0", layout="wide")
st.title("🚀 Crypto Signal Dashboard v4.6.0 – Final Styled Cards")

def mock_signals():
    return [
        {
            "symbol": "WETH",
            "name": "Wrapped Ethereum",
            "buy_score": 62.8,
            "current_price": 1791.68,
            "buy_range": (1764.80, 1818.56),
            "logo_url": "https://assets.coingecko.com/coins/images/2518/thumb/weth.png",
            "indicators": {"RSI": 63, "MACD": 30, "EMA": 100, "Volume": 100, "StochRSI": 30, "ADX": 30},
            "analysis": "MACD is flat or bearish, offering no clear signal. ADX suggests trend strength is moderate or weak. RSI for WETH is neutral, showing room for movement. Volume is surging above average, confirming strong interest."
        },
        {
            "symbol": "SOL",
            "name": "Solana",
            "buy_score": 74.1,
            "current_price": 145.32,
            "buy_range": (143.00, 147.65),
            "logo_url": "https://assets.coingecko.com/coins/images/4128/thumb/solana.png",
            "indicators": {"RSI": 70, "MACD": 60, "EMA": 100, "Volume": 90, "StochRSI": 50, "ADX": 40},
            "analysis": "Solana shows strong momentum with bullish RSI and MACD. EMA is supportive and volume is confirming upward pressure. Traders may find confidence in this breakout setup."
        }
    ]

signals = mock_signals()
cols = st.columns(2)
for i, sig in enumerate(signals):
    with cols[i % 2]:
        display_signal_card(sig)
