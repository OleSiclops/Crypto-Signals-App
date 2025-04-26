# streamlit_test_indicators.py

import streamlit as st
import pandas as pd
from indicator_engine import IndicatorEngine

st.title("🚀 Indicator Engine Testing (v2.2-v2.3)")

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
scores = engine.generate_score()

st.subheader("📈 Latest Indicator Outputs:")
for key, value in latest_signals.items():
    st.write(f"**{key}:** {value:.2f}")

st.subheader("🏆 Indicator Scores:")
for key, value in scores.items():
    st.write(f"**{key}:** {value:.2f}")
