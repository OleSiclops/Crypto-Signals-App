
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
            if 'volume' not in self.df.columns:
                return None
            avg_vol = self.df['volume'].rolling(window=20).mean()
            current_vol = self.df['volume'].iloc[-1]
            if current_vol > avg_vol.iloc[-1] * 1.3:
                return 100
            elif current_vol > avg_vol.iloc[-1]:
                return 60
            else:
                return 30
        except:
            return None

    def calculate_stoch_rsi(self):
        try:
            stoch_rsi = ta.momentum.StochRSIIndicator(close=self.df['close']).stochrsi_k()
            if stoch_rsi.iloc[-2] < 0.2 and stoch_rsi.iloc[-1] > 0.2:
                return 100
            else:
                return 30
        except:
            return None

    def calculate_adx(self):
        try:
            adx = ta.trend.ADXIndicator(high=self.df['high'], low=self.df['low'], close=self.df['close']).adx()
            latest_adx = adx.iloc[-1]
            if latest_adx > 25:
                return 100
            elif latest_adx > 20:
                return 60
            else:
                return 30
        except:
            return None

    def calculate_all(self):
        self.scores['RSI'] = self.calculate_rsi()
        self.scores['MACD'] = self.calculate_macd()
        self.scores['EMA'] = self.calculate_ema_trend()
        self.scores['Volume'] = self.calculate_volume_spike()
        self.scores['StochRSI'] = self.calculate_stoch_rsi()
        self.scores['ADX'] = self.calculate_adx()
        return self.scores

    def calculate_weighted_score(self):
        weights = {
            'RSI': 0.25,
            'MACD': 0.25,
            'EMA': 0.20,
            'Volume': 0.15,
            'StochRSI': 0.10,
            'ADX': 0.05
        }
        total = 0
        weight_total = 0
        for k, w in weights.items():
            if self.scores.get(k) is not None:
                total += self.scores[k] * w
                weight_total += w
        return round(total / weight_total, 2) if weight_total > 0 else 0.0
