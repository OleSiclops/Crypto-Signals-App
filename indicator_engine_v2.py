
import pandas as pd
import numpy as np
import ta

class IndicatorEngineV2:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df.dropna(inplace=True)
        self.scores = {}

    def calculate_rsi(self):
        try:
            rsi = ta.momentum.RSIIndicator(close=self.df['close'], window=14).rsi()
            latest_rsi = rsi.dropna().iloc[-1]
            score = max(0, min(100, (70 - latest_rsi) * (100 / 40)))
            return round(score, 2)
        except:
            return None

    def calculate_macd(self):
        try:
            macd = ta.trend.MACD(close=self.df['close'])
            macd_line = macd.macd()
            signal_line = macd.macd_signal()
            if macd_line.iloc[-2] < signal_line.iloc[-2] and macd_line.iloc[-1] > signal_line.iloc[-1]:
                return 100
            else:
                return 30
        except:
            return None

    def calculate_ema_trend(self):
        try:
            ema = ta.trend.EMAIndicator(close=self.df['close'], window=50).ema_indicator()
            if self.df['close'].iloc[-1] > ema.iloc[-1]:
                return 100
            else:
                return 30
        except:
            return None

    def calculate_volume_spike(self):
        try:
            if "volume" not in self.df.columns or self.df["volume"].isna().all():
                print("⚠️ No volume data found in DataFrame.")
                return 0
            recent_volume = self.df["volume"].iloc[-1]
            avg_volume = self.df["volume"].rolling(window=5).mean().iloc[-2]
            if pd.isna(recent_volume) or pd.isna(avg_volume) or avg_volume == 0:
                print("⚠️ Invalid volume values (NaN or zero).")
                return 0
            spike_ratio = (recent_volume / avg_volume) * 100
            return min(spike_ratio, 100)
        except Exception as e:
            print(f"Volume spike calc error: {e}")
            return 0
def calculate_stoch_rsi(self):
        try:
            stoch_rsi = ta.momentum.StochRSIIndicator(close=self.df['close']).stochrsi_k()
            if stoch_rsi.iloc[-2] < 0.2 and stoch_rsi.iloc[-1] > 0.2:
                return 100
            else:
                return 30
        except:
            return None
