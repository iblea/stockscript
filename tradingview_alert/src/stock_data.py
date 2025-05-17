import json

"""
{'type': 'alert', 'time': '2025-05-16T10:20:30Z', 'timenow': '2025-05-16T10:21:00Z', 'ticker': 'NQ1!', 'exchange': 'CME_MINI', 'interval': ' 30S', 'data': {'open': '21447.25', 'close': '21446.75', 'low': '21444.5', 'high': '21447.5', 'volume': '80'}, 'current': 'USD', 'base': ''}
{'type': 'alert', 'time': '2025-05-16T10:20:30Z', 'timenow': '2025-05-16T10:21:05Z', 'ticker': 'ES1!', 'exchange': 'CME_MINI', 'interval': ' 30S', 'data': {'open': '5947.25', 'close': '5947.25', 'low': '5947', 'high': '5947.25', 'volume': '130'}, 'current': 'USD', 'base': ''}
{'type': 'alert', 'time': '2025-05-16T10:20:30Z', 'timenow': '2025-05-16T10:21:01Z', 'ticker': 'GC1!', 'exchange': 'COMEX', 'interval': ' 30S', 'data': {'open': '3205.5', 'close': '3205', 'low': '3204.4', 'high': '3206.2', 'volume': '54'}, 'current': 'USD', 'base': ''}
{'type': 'alert', 'time': '2025-05-16T10:20:30Z', 'timenow': '2025-05-16T10:21:10Z', 'ticker': 'BTCUSD', 'exchange': 'BINANCE', 'interval': ' 30S', 'data': {'open': '103860.58', 'close': '103808.68', 'low': '103803.53', 'high': '103860.58', 'volume': '0.01156'}, 'current': 'USD', 'base': 'BTC'}
"""

class StockPrice:
    open: float = 0.0
    close: float = 0.0
    low: float = 0.0
    high: float = 0.0
    volume: float = 0.0

    def __init__(self):
        self.open = 0.0
        self.close = 0.0
        self.low = 0.0
        self.high = 0.0
        self.volume = 0.0

    def __init__(self, open: float, close: float, low: float, high: float, volume: float):
        self.open = open
        self.close = close
        self.low = low
        self.high = high
        self.volume = volume

    def __repr__(self):
        return '{{ "open": {}, "close": {}, "low": {}, "high": {}, "volume": {} }}'.format(
            self.open,
            self.close,
            self.low,
            self.high,
            self.volume
        )

    def __str__(self):
        return f"StockPrice(open={self.open}, close={self.close}, low={self.low}, high={self.high}, volume={self.volume})"

    def getOpen(self) -> float:
        return self.open
    def getClose(self) -> float:
        return self.close
    def getLow(self) -> float:
        return self.low
    def getHigh(self) -> float:
        return self.high
    def getVolume(self) -> float:
        return self.volume
    def getPrice(self) -> float:
        return self.close

class StockData:
    time = ""
    timenow = ""
    ticker: str = ""
    exchange: str = ""
    interval: str = ""
    data: StockPrice = StockPrice()
    current: str = ""
    base: str = ""

    def __init__(self):
        self.time = ""
        self.timenow = ""
        self.ticker = ""
        self.exchange = ""
        self.interval = ""
        self.data = StockPrice()
        self.current = ""
        self.base = ""

    def __init__(self, json_string: str):
        jsonData = json.loads(json_string)

        self.time = jsonData['time']
        self.timenow = jsonData['timenow']
        self.ticker = jsonData['ticker']
        self.exchange = jsonData['exchange']
        self.interval = jsonData['interval']
        self.data = StockPrice(
            float(jsonData['data']['open']),
            float(jsonData['data']['close']),
            float(jsonData['data']['low']),
            float(jsonData['data']['high']),
            float(jsonData['data']['volume'])
        )
        self.current = jsonData['current']
        self.base = jsonData['base']

    def __init__(self, time: str, timenow: str, ticker: str, exchange: str, interval: str, data: StockPrice, current: str, base: str):
        self.time = time
        self.timenow = timenow
        self.ticker = ticker
        self.exchange = exchange
        self.interval = interval
        self.data = data
        self.current = current
        self.base = base


    def returnString(self) -> str:
        ret = f"ticker: \"{self.ticker}\" [{self.exchange}]\n"
        ret += f"price: {self.data.getPrice()}\n"
        ret += f"candle time: {self.time}\n"
        ret += f"now: {self.timenow}\n"
        ret += f"  - open: {self.data.getOpen()}\n"
        ret += f"  - close: {self.data.getClose()}\n"
        ret += f"  - low: {self.data.getLow()}\n"
        ret += f"  - high: {self.data.getHigh()}\n"
        ret += f"  - volume: {self.data.getVolume()}\n"
        ret += f"interval: {self.interval}\n"
        ret += f"currency type: \"{self.current}\", base: \"{self.base}\""
        return ret

    def __repr__(self):
        return '{{ "time": "{}", "timenow": "{}", "ticker": "{}", "exchange": "{}", "interval": "{}", "data": {}, "current": "{}", "base": "{}" }}'.format(
            self.time,
            self.timenow,
            self.ticker,
            self.exchange,
            self.interval,
            self.data.__repr__(),
            self.current,
            self.base
        )

    def __str__(self):
        return self.returnString()


