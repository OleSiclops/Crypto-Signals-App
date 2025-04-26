
# indicator_engine.py

import pandas as pd
import numpy as np
import ta  # Technical Analysis library (pip install ta)

class IndicatorEngine:
    def __init__(self, ohlc_data: pd.DataFrame):
        self.df = ohlc_data.copy()
        self._prepare_data()

    def _prepare_data(self):
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], unit='ms', errors='coerce')
        self.df.set_index('timestamp', inplace=True)

    def calculate_rsi(self, period=14):
        self.df['rsi'] = ta.momentum.RSIIndicator(close=self.df['close'], window=period).rsi()

    def calculate_stoch_rsi(self):
        stoch_rsi = ta.momentum.StochRSIIndicator(close=self.df['close'])
        self.df['stoch_rsi_k'] = stoch_rsi.stochrsi_k()
        self.df['stoch_rsi_d'] = stoch_rsi.stochrsi_d()

    def calculate_ema(self, span=9):
        self.df[f'ema_{span}'] = self.df['close'].ewm(span=span, adjust=False).mean()

    def calculate_ema_crossover(self, short_span=9, long_span=21):
        self.calculate_ema(short_span)
        self.calculate_ema(long_span)
        self.df['ema_crossover'] = self.df[f'ema_{short_span}'] - self.df[f'ema_{long_span}']

    def calculate_bollinger_band_width(self, window=20, std=2):
        bb_indicator = ta.volatility.BollingerBands(close=self.df['close'], window=window, window_dev=std)
        self.df['bb_width'] = bb_indicator.bollinger_hband() - bb_indicator.bollinger_lband()

    def calculate_volume_change(self):
        self.df['volume_change_pct'] = self.df['volume'].pct_change() * 100

    def calculate_vwap(self):
        cumulative_vp = (self.df['volume'] * (self.df['high'] + self.df['low'] + self.df['close']) / 3).cumsum()
        cumulative_volume = self.df['volume'].cumsum()
        self.df['vwap'] = cumulative_vp / cumulative_volume

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
        return latest.to_dict()
