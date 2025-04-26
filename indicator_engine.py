# indicator_engine.py

import pandas as pd
import numpy as np
import ta

class IndicatorEngine:
    def __init__(self, ohlc_data: pd.DataFrame):
        self.df = ohlc_data.copy()
        self._prepare_data()

    def _prepare_data(self):
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], unit='ms', errors='coerce')
        self.df.set_index('timestamp', inplace=True)

    def calculate_rsi(self, period=14):
        try:
            self.df['rsi'] = ta.momentum.RSIIndicator(close=self.df['close'], window=period).rsi()
        except Exception as e:
            print(f"RSI calculation error: {e}")

    def calculate_stoch_rsi(self):
        try:
            stoch_rsi = ta.momentum.StochRSIIndicator(close=self.df['close'])
            self.df['stoch_rsi_k'] = stoch_rsi.stochrsi_k()
            self.df['stoch_rsi_d'] = stoch_rsi.stochrsi_d()
        except Exception as e:
            print(f"Stochastic RSI calculation error: {e}")

    def calculate_ema(self, span=9):
        try:
            self.df[f'ema_{span}'] = self.df['close'].ewm(span=span, adjust=False).mean()
        except Exception as e:
            print(f"EMA {span} calculation error: {e}")

    def calculate_ema_crossover(self, short_span=9, long_span=21):
        self.calculate_ema(short_span)
        self.calculate_ema(long_span)
        try:
            self.df['ema_crossover'] = self.df[f'ema_{short_span}'] - self.df[f'ema_{long_span}']
        except Exception as e:
            print(f"EMA Crossover calculation error: {e}")

    def calculate_bollinger_band_width(self, window=20, std=2):
        try:
            bb_indicator = ta.volatility.BollingerBands(close=self.df['close'], window=window, window_dev=std)
            self.df['bb_width'] = bb_indicator.bollinger_hband() - bb_indicator.bollinger_lband()
        except Exception as e:
            print(f"Bollinger Band Width calculation error: {e}")

    def calculate_volume_change(self):
        try:
            self.df['volume_change_pct'] = self.df['volume'].pct_change() * 100
        except Exception as e:
            print(f"Volume Change calculation error: {e}")

    def calculate_vwap(self):
        try:
            cumulative_vp = (self.df['volume'] * (self.df['high'] + self.df['low'] + self.df['close']) / 3).cumsum()
            cumulative_volume = self.df['volume'].cumsum()
            self.df['vwap'] = cumulative_vp / cumulative_volume
        except Exception as e:
            print(f"VWAP calculation error: {e}")

    def run_all_indicators(self):
        self.calculate_rsi()
        self.calculate_stoch_rsi()
        self.calculate_ema(9)
        self.calculate_ema_crossover(9, 21)
        self.calculate_bollinger_band_width()
        self.calculate_volume_change()
        self.calculate_vwap()

    def get_latest_indicators(self):
        latest = self.df.iloc[-1]
        return latest.dropna().to_dict()
