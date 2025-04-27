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

    def generate_score(self, debug=False):
        latest = self.get_latest_indicators()
        scores = {}

        if 'rsi' in latest:
            rsi = latest['rsi']
            scores['rsi_score'] = max(0, min(100, (70 - rsi) * (100 / 40)))

        if 'stoch_rsi_k' in latest:
            stoch_k = latest['stoch_rsi_k']
            scores['stoch_rsi_score'] = max(0, min(100, (100 - stoch_k)))

        if 'ema_crossover' in latest:
            crossover = latest['ema_crossover']
            scores['ema_crossover_score'] = max(0, min(100, crossover * 5))

        if 'bb_width' in latest:
            bb_width = latest['bb_width']
            scores['bb_width_score'] = max(0, min(100, 100 - bb_width))

        if 'volume_change_pct' in latest:
            volume_change = latest['volume_change_pct']
            scores['volume_change_score'] = max(0, min(100, volume_change))

        if 'vwap' in latest and 'close' in latest:
            if latest['close'] > latest['vwap']:
                scores['vwap_bias_score'] = 100
            else:
                scores['vwap_bias_score'] = 0

        if scores:
            total_score = sum(scores.values()) / len(scores)
        else:
            total_score = 0

        scores['total_score'] = total_score

        if debug:
            return scores
        else:
            return {"total_score": total_score}

    def generate_signal(self, debug=False):
        scores = self.generate_score(debug=debug)
        total_score = scores.get('total_score', 0)

        if total_score >= 70:
            signal = "BUY"
            reason = f"Strong bullish technicals detected (Score: {total_score:.2f})."
        elif 50 <= total_score < 70:
            signal = "WATCH"
            reason = f"Moderate technical strength — monitor for improvement (Score: {total_score:.2f})."
        else:
            signal = "NO TRADE"
            reason = f"Weak technicals — no action recommended (Score: {total_score:.2f})."

        return {
            "signal": signal,
            "reason": reason,
            "score": total_score
        }
