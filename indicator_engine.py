
import pandas as pd
import ta

class IndicatorEngine:
    def __init__(self, ohlc_data: pd.DataFrame):
        self.df = ohlc_data.copy()
        self._prepare_data()

    def _prepare_data(self):
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], unit='ms', errors='coerce')
        self.df.set_index('timestamp', inplace=True)

    def calculate_rsi(self, period=14):
        self.df['rsi'] = ta.momentum.RSIIndicator(close=self.df['close'], window=period).rsi()

    def run_all_indicators(self):
        self.calculate_rsi()

    def generate_score(self):
        latest = self.df.iloc[-1]
        rsi = latest.get("rsi", 0)
        score = max(0, min(100, (70 - rsi) * (100 / 40)))
        return round(score, 2), rsi

    def generate_paragraph(self, name, score, rsi, gain):
        paragraphs = [
            f"{name} is currently demonstrating strong bullish momentum with an RSI of {rsi:.1f}. The coin has gained {gain:.2f}% recently, suggesting robust market strength.",
            f"Recent technical indicators show {name} advancing with an RSI of {rsi:.1f} and a price increase of {gain:.2f}%. Buying pressure appears sustained and growing.",
            f"{name} is gaining positive momentum, with its RSI at {rsi:.1f} and a {gain:.2f}% increase observed. Market conditions favor a continuation of this trend.",
            f"With an RSI of {rsi:.1f} and a {gain:.2f}% gain, {name} is breaking through resistance levels. Momentum indicators suggest a strong bullish outlook."
        ]
        import random
        return random.choice(paragraphs)
