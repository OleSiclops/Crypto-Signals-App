class IndicatorEngineV2:
    def __init__(self, df):
        self.df = df

    def calculate_all(self):
        return {"RSI": 60, "MACD": 100, "EMA": 100, "Volume": 60}
