import json
from datetime import datetime
from config import DATA_DIR

from os.path import exists

STOCK_DATA_PATH = DATA_DIR + "stock_data.json"

class StockPrice:
    open: float = 0.0
    close: float = 0.0
    low: float = 0.0
    high: float = 0.0
    volume: float = 0.0

    def __init__(self, open: float, close: float, low: float, high: float, volume: float):
        self.open = open
        self.close = close
        self.low = low
        self.high = high
        self.volume = volume

    @staticmethod
    def default():
        return StockPrice(0.0, 0.0, 0.0, 0.0, 0.0)

    def __repr__(self):
        return '{{ "open": "{}", "close": "{}", "low": "{}", "high": "{}", "volume": "{}" }}'.format(
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
    time: datetime = datetime.min
    timenow: datetime = datetime.min
    ticker: str = ""
    exchange: str = ""
    interval: str = ""
    data: StockPrice = StockPrice.default()
    current: str = ""
    base: str = ""

    def __init__(self, time: str, timenow: str, ticker: str, exchange: str, interval: str, data: StockPrice, current: str, base: str):
        self.time = self.getTime(time)
        self.timenow = self.getTime(timenow)
        self.ticker = ticker
        self.exchange = exchange
        self.interval = interval
        self.data = data
        self.current = current
        self.base = base

    @staticmethod
    def default():
        return StockData("", "", "", "", "", StockPrice.default(), "", "")

    @staticmethod
    def setDict(jsonData: dict):
        # {'type': 'alert', 'time': '2025-05-16T10:20:30Z', 'timenow': '2025-05-16T10:21:00Z', 'ticker': 'NQ1!', 'exchange': 'CME_MINI', 'interval': ' 30S', 'data': {'open': '21447.25', 'close': '21446.75', 'low': '21444.5', 'high': '21447.5', 'volume': '80'}, 'current': 'USD', 'base': ''}
        time = jsonData.get('time', "")
        timenow = jsonData.get('timenow', "")
        ticker = jsonData.get('ticker', "")
        exchange = jsonData.get('exchange', "")
        interval = jsonData.get('interval', "")
        if 'data' in jsonData:
            open_price: str = jsonData['data'].get('open', "0.0")
            close_price: str = jsonData['data'].get('close', "0.0")
            low_price: str = jsonData['data'].get('low', "0.0")
            high_price: str = jsonData['data'].get('high', "0.0")
            volume: str = jsonData['data'].get('volume', "0.0")
            data = StockPrice(
                float(open_price),
                float(close_price),
                float(low_price),
                float(high_price),
                float(volume)
            )
        else:
            data = StockPrice()

        current = jsonData.get('current', "")
        base = jsonData.get('base', "")
        return StockData(time, timenow, ticker, exchange, interval, data, current, base)

    def getDict(self) -> dict:
        return {
            "time": self.time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timenow": self.timenow.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ticker": self.ticker,
            "exchange": self.exchange,
            "interval": self.interval,
            "data": {
                "open": str(self.data.getOpen()),
                "close": str(self.data.getClose()),
                "low": str(self.data.getLow()),
                "high": str(self.data.getHigh()),
                "volume": str(self.data.getVolume())
            },
            "current": self.current,
            "base": self.base
        }

    def getTime(self, time_string: str = "") -> datetime:
        if time_string is None or len(time_string) == 0:
            return datetime.min
        datetime_obj = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%SZ")
        return datetime_obj

    def getPrice(self) -> float:
        return self.data.getPrice()

    def returnString(self) -> str:
        ret = f"ticker: \"{self.ticker}\" [{self.exchange}]\n"
        ret += f"price: {self.getPrice()}\n"
        ret += f"candle time: {self.time.strftime("%Y-%m%d %H:%M:%S")}\n"
        ret += f"now: {self.timenow.strftime("%Y-%m%d %H:%M:%S")}\n"
        ret += "```\n"
        ret += f"  - close: {self.data.getClose()}\n"
        ret += f"  - open : {self.data.getOpen()}\n"
        ret += f"  - low  : {self.data.getLow()}\n"
        ret += f"  - high : {self.data.getHigh()}\n"
        ret += f"  - volume: {self.data.getVolume()}\n"
        ret += "```\n"
        ret += f"interval: {self.interval}\n"
        ret += f"currency type: \"{self.current}\", base: \"{self.base}\""
        return ret

    def __repr__(self):
        return '{{ "time": "{}", "timenow": "{}", "ticker": "{}", "exchange": "{}", "interval": "{}", "data": {}, "current": "{}", "base": "{}" }}'.format(
            self.time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            self.timenow.strftime("%Y-%m-%dT%H:%M:%SZ"),
            self.ticker,
            self.exchange,
            self.interval,
            self.data.__repr__(),
            self.current,
            self.base
        )

    def __str__(self):
        return self.returnString()


stock_data_dict: dict[str, StockData] = {}

"""
{'type': 'alert', 'time': '2025-05-16T10:20:30Z', 'timenow': '2025-05-16T10:21:05Z', 'ticker': 'ES1!', 'exchange': 'CME_MINI', 'interval': ' 30S', 'data': {'open': '5947.25', 'close': '5947.25', 'low': '5947', 'high': '5947.25', 'volume': '130'}, 'current': 'USD', 'base': ''}
{'type': 'alert', 'time': '2025-05-16T10:20:30Z', 'timenow': '2025-05-16T10:21:01Z', 'ticker': 'GC1!', 'exchange': 'COMEX', 'interval': ' 30S', 'data': {'open': '3205.5', 'close': '3205', 'low': '3204.4', 'high': '3206.2', 'volume': '54'}, 'current': 'USD', 'base': ''}
{'type': 'alert', 'time': '2025-05-16T10:20:30Z', 'timenow': '2025-05-16T10:21:10Z', 'ticker': 'BTCUSD', 'exchange': 'BINANCE', 'interval': ' 30S', 'data': {'open': '103860.58', 'close': '103808.68', 'low': '103803.53', 'high': '103860.58', 'volume': '0.01156'}, 'current': 'USD', 'base': 'BTC'}
"""




def save_stockdata_in_memory(json_data: dict) -> bool:
    global stock_data_dict

    if json_data is None:
        print("Error: json_data is None")
        return False
    if json_data.get('type', "") != "alert":
        print("Error: json_data['type'] != 'alert'")
        return False

    ticker = json_data.get('ticker', "").lower()
    data = StockData.setDict(json_data)
    stock_data_dict[ticker] = data
    return True

def get_stockdata_string(ticker: str) -> str:
    global stock_data_dict

    if not stock_data_dict:
        return "no stock data"

    if ticker == "":
        return get_all_stockdata_string()

    if ticker in stock_data_dict:
        return str(stock_data_dict[ticker])
    else:
        return ""

def get_all_stockdata_string() -> str:
    global stock_data_dict

    if not stock_data_dict:
        return "no stock data"

    string = ""
    for ticker in stock_data_dict:
        data = stock_data_dict[ticker]
        string += "ticker: " + data.ticker + "\n"
        string += "price: " + str(data.getPrice()) + "\n"
        string += "time: " + str(data.time) + "\n\n"

    return string


def save_stockdata_in_disk() -> None:
    global stock_data_dict

    dic = {}
    for ticker in stock_data_dict:
        data = stock_data_dict[ticker]
        dic[ticker] = data.getDict()

    json_string = json.dumps(dic, indent=4)

    with open(STOCK_DATA_PATH, 'w') as f:
        f.write(json_string)
    # print(f"Saved stock data to {STOCK_DATA_PATH}")


def load_stockdata_from_disk() -> bool:
    global stock_data_dict

    if exists(STOCK_DATA_PATH) is False:
        print(f"File not found: {STOCK_DATA_PATH}")
        return False

    json_data: dict = {}
    try:
        with open(STOCK_DATA_PATH, 'r') as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return False

    stock_data_dict.clear()
    for ticker in json_data:
        data = json_data[ticker]
        stock_data_dict[ticker] = StockData.setDict(data)

    return True
