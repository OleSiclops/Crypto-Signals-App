
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

    def generate_score(self, debug=False):
        latest = self.df.iloc[-1]
        scores = {}
        if 'rsi' in latest:
            rsi = latest['rsi']
            scores['rsi_score'] = max(0, min(100, (70 - rsi) * (100 / 40)))
        total_score = sum(scores.values()) / len(scores) if scores else 0
        scores['total_score'] = total_score
        if debug:
            return scores
        else:
            return {"total_score": total_score}

    def generate_signal(self, debug=False):
        scores = self.generate_score(debug=debug)
        total_score = scores.get('total_score', 0)
        if total_score >= 70:
            return {"signal": "BUY", "reason": "Strong bullish technicals."}
        elif 50 <= total_score < 70:
            return {"signal": "WATCH", "reason": "Moderate technicals."}
        else:
            return {"signal": "NO TRADE", "reason": "Weak technicals."}
