import json
from os.path import exists
from config import DATA_DIR
import stock_data
import alert_manager

REALTIME_DATA_PATH = DATA_DIR + "realtime.json"

# 메모리에 저장된 realtime 티커 목록
realtime_tickers: list = []


def set_realtime_tickers(tickers: list[str]) -> tuple[bool, str]:
    """
    realtime 티커 목록 설정
    Returns: (성공 여부, 메시지)
    """
    global realtime_tickers

    # 빈 리스트도 허용 (realtime off)
    if not isinstance(tickers, list):
        return False, "티커 목록은 리스트 형태여야 합니다"

    # 소문자로 변환하고 stock_data에 있는 것만 필터링
    valid_tickers = []
    invalid_tickers = []

    for ticker in tickers:
        ticker_lower = ticker.lower()
        if ticker_lower in stock_data.stock_data_dict:
            valid_tickers.append(ticker_lower)
        else:
            invalid_tickers.append(ticker)

    realtime_tickers = valid_tickers
    save_realtime_to_disk()

    msg = ""
    if valid_tickers:
        msg = f"Realtime 티커 설정 완료: {', '.join([t.upper() for t in valid_tickers])}"
    else:
        msg = "Realtime 표시가 비활성화되었습니다"

    if invalid_tickers:
        msg += f"\n(무시된 티커: {', '.join([t.upper() for t in invalid_tickers])})"

    return True, msg


def get_realtime_message() -> str:
    """
    realtime 메시지 생성 (Markdown 형식)
    """
    global realtime_tickers

    if not realtime_tickers:
        return ""

    msg = ""

    for ticker in realtime_tickers:
        # ticker가 stock_data에 없으면 스킵
        if ticker not in stock_data.stock_data_dict:
            continue

        stock = stock_data.stock_data_dict[ticker]
        current_price = stock.getPrice()

        # Markdown 헤더로 티커명 표시
        msg += f"## {ticker.upper()}\n"
        msg += f"**{current_price}**\n"
        msg += f"time: {stock.time.strftime('%Y-%m-%d %H:%M:%S')}\n"

        # alert 정보 확인
        if ticker in alert_manager.alert_data:
            alert_info = alert_manager.alert_data[ticker]
            target_price = alert_info.get("target_price")
            stop_loss_price = alert_info.get("stop_loss_price")
            purchased_price = alert_info.get("purchased_price")
            purchased_quantity = alert_info.get("purchased_quantity")

            # target과 stoploss 정보 표시
            target_str = str(target_price) if target_price is not None else "-"
            stoploss_str = str(stop_loss_price) if stop_loss_price is not None else "-"
            msg += f"target: {target_str} / stoploss: {stoploss_str}\n"

            # purchased 정보가 있으면 손익 표시
            if purchased_price is not None and purchased_quantity is not None:
                usd_profit, krw_profit = stock_data.calculate_profit(
                    ticker, purchased_price, purchased_quantity, current_price
                )

                msg += f"purchased: {purchased_price} (x {purchased_quantity})"

                if usd_profit is not None and krw_profit is not None:
                    msg += f" {{ usd: {usd_profit:,.2f}, krw: {krw_profit:,.0f} }}"

                msg += "\n"

        msg += "\n"

    return msg.strip()


def save_realtime_to_disk() -> None:
    """realtime 데이터를 파일에 저장"""
    global realtime_tickers

    data = {
        "realtime": realtime_tickers
    }

    json_string = json.dumps(data, indent=4)

    with open(REALTIME_DATA_PATH, 'w') as f:
        f.write(json_string)


def load_realtime_from_disk() -> bool:
    """파일에서 realtime 데이터 로드"""
    global realtime_tickers

    if not exists(REALTIME_DATA_PATH):
        print(f"Realtime file not found: {REALTIME_DATA_PATH}")
        # 파일이 없으면 빈 리스트로 초기화하고 파일 생성
        realtime_tickers = []
        save_realtime_to_disk()
        return True

    try:
        with open(REALTIME_DATA_PATH, 'r') as f:
            data = json.load(f)

        realtime_tickers = data.get("realtime", [])
        return True
    except Exception as e:
        print(f"Error loading realtime data: {e}")
        # 에러 발생 시 빈 리스트로 초기화
        realtime_tickers = []
        return False
