import json
from datetime import datetime, timedelta
from config import DATA_DIR

from os.path import exists, getmtime

STOCK_DATA_PATH = DATA_DIR + "stock_data.json"
TICK_DATA_PATH = DATA_DIR + "tick.json"


def utc_to_kst(utc_time: datetime) -> datetime:
    """UTC 시간을 KST(한국 시간)로 변환 (+9시간)"""
    if utc_time == datetime.min:
        return utc_time
    return utc_time + timedelta(hours=9)


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
        import alert_manager

        ret = f"ticker: \"{self.ticker}\" [{self.exchange}]\n"
        ret += f"price: {self.getPrice()}\n"
        ret += f"candle time: {utc_to_kst(self.time).strftime('%Y-%m-%d %H:%M:%S')} KST\n"
        ret += f"now: {utc_to_kst(self.timenow).strftime('%Y-%m-%d %H:%M:%S')} KST\n"
        ret += "```\n"
        ret += f"  - close: {self.data.getClose()}\n"
        ret += f"  - open : {self.data.getOpen()}\n"
        ret += f"  - low  : {self.data.getLow()}\n"
        ret += f"  - high : {self.data.getHigh()}\n"
        ret += f"  - volume: {self.data.getVolume()}\n"
        ret += "```\n"
        ret += f"interval: {self.interval}\n"
        ret += f"currency type: \"{self.current}\", base: \"{self.base}\"\n"

        # alert 정보 확인
        ticker_lower = self.ticker.lower()
        if ticker_lower in alert_manager.alert_data:
            alert_info = alert_manager.alert_data[ticker_lower]
            purchased_price = alert_info.get("purchased_price")
            purchased_quantity = alert_info.get("purchased_quantity")
            target_price = alert_info.get("target_price")
            stop_loss_price = alert_info.get("stop_loss_price")

            # alert 정보가 있으면 표시
            ret += "```\n"

            # purchased 정보 표시 (있는 경우에만)
            if purchased_price is not None and purchased_quantity is not None:
                ret += f"purchased: {purchased_price} (x {purchased_quantity})\n"

            # target 정보 표시
            if target_price is not None:
                ret += f"target   : {target_price}\n"
            else:
                ret += f"target   : -\n"

            # stoploss 정보 표시
            if stop_loss_price is not None:
                ret += f"stoploss : {stop_loss_price}\n"
            else:
                ret += f"stoploss : -\n"

            # 손익 계산 (purchased 정보가 있는 경우에만)
            if purchased_price is not None and purchased_quantity is not None:
                current_price = self.getPrice()
                usd_profit, krw_profit = calculate_profit(self.ticker, purchased_price, purchased_quantity, current_price)

                if usd_profit is not None and krw_profit is not None:
                    ret += f"usd      : {usd_profit:,.2f}\n"
                    ret += f"krw      : {krw_profit:,.0f}\n"
                else:
                    ret += f"usd      : null\n"
                    ret += f"krw      : null\n"

            ret += "```\n"
            ret += f"current price: {self.getPrice()}"

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
tick_data_dict: dict = {}
tick_last_load_time: float = 0.0  # tick.json 마지막 로드 시간

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
        return "no stock data in ticker: " + ticker

def get_all_stockdata_string() -> str:
    global stock_data_dict
    import alert_manager

    if not stock_data_dict:
        return "no stock data"

    string = ""
    for ticker in stock_data_dict:
        data = stock_data_dict[ticker]
        string += "ticker: " + data.ticker + "\n"
        string += "price: " + str(data.getPrice()) + "\n"
        string += "time: " + utc_to_kst(data.time).strftime('%Y-%m-%d %H:%M:%S') + " KST\n"

        # alert 정보 확인
        ticker_lower = ticker.lower()
        if ticker_lower in alert_manager.alert_data:
            alert_info = alert_manager.alert_data[ticker_lower]
            target_price = alert_info.get("target_price")
            stop_loss_price = alert_info.get("stop_loss_price")
            purchased_price = alert_info.get("purchased_price")
            purchased_quantity = alert_info.get("purchased_quantity")

            # target과 stoploss 정보 표시 (무조건)
            target_str = str(target_price) if target_price is not None else "-"
            stoploss_str = str(stop_loss_price) if stop_loss_price is not None else "-"
            string += f"target: {target_str} / stoploss: {stoploss_str}\n"

            # purchased 정보가 있으면 손익 표시
            if purchased_price is not None and purchased_quantity is not None:
                # 손익 계산
                current_price = data.getPrice()
                usd_profit, krw_profit = calculate_profit(ticker, purchased_price, purchased_quantity, current_price)

                string += f"purchased: {purchased_price} (x {purchased_quantity})"

                if usd_profit is not None and krw_profit is not None:
                    string += f" {{ usd: {usd_profit:,.2f}, krw: {krw_profit:,.0f} }}"

                string += "\n"

        string += "\n"

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


def load_tickdata_from_disk() -> bool:
    global tick_data_dict, tick_last_load_time
    import time

    if not exists(TICK_DATA_PATH):
        print(f"Tick file not found: {TICK_DATA_PATH}")
        return False

    try:
        with open(TICK_DATA_PATH, 'r') as f:
            tick_data_dict = json.load(f)
        tick_last_load_time = time.time()  # 로드 시간 기록
        return True
    except Exception as e:
        print(f"Error loading tick data: {e}")
        return False


def check_and_reload_tick_data() -> bool:
    """
    tick.json 파일의 수정 시간을 체크하고 필요하면 재로드
    Returns: 재로드 여부
    """
    global tick_last_load_time

    if not exists(TICK_DATA_PATH):
        return False

    try:
        # 파일의 마지막 수정 시간
        file_mtime = getmtime(TICK_DATA_PATH)

        # 마지막 로드 시간보다 파일이 더 최근에 수정되었으면 재로드
        if file_mtime > tick_last_load_time:
            print(f"Tick data file has been modified. Reloading...")
            return load_tickdata_from_disk()

        return False
    except Exception as e:
        print(f"Error checking tick data file: {e}")
        return False


def calculate_profit(ticker: str, purchased_price: float, purchased_quantity: int, current_price: float) -> tuple[float | None, float | None]:
    """
    손익 계산
    Returns: (usd 수익, krw 수익)
    """
    global tick_data_dict

    ticker = ticker.lower()

    # tick_data에 티커 정보가 없으면 None 반환
    if ticker not in tick_data_dict:
        return None, None

    tick_info = tick_data_dict[ticker]
    tickrate = tick_info.get("tick", 0)
    usd_per_tick = tick_info.get("usd", 0)
    krw_per_tick = tick_info.get("krw", 0)

    if tickrate == 0:
        return None, None

    # 손익 계산: ((현재가 - 구매가) / tickrate) * 구매수량 * (usd or krw)
    price_diff = current_price - purchased_price
    tick_count = price_diff / tickrate
    total_profit_usd = tick_count * purchased_quantity * usd_per_tick
    total_profit_krw = tick_count * purchased_quantity * krw_per_tick

    return total_profit_usd, total_profit_krw
