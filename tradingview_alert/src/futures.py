import os
from typing import List
import json


POS_ERROR = 0
# 주문 포지션 (진입)
POS_ENTRY = 1
# 주문 포지션 (청산)
POS_CLOSE = 2

TYPE_ERROR = 0
# 주문 타입 (롱)
TYPE_LONG = 1
# 주문 타입 (숏)
TYPE_SHORT = 2

SCRIPT_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data/"
DATA_FILE: str = "data.json"
DATA_FULL_PATH: str = os.path.join(SCRIPT_DIR, DATA_FILE)


def get_data_hdd() -> dict:

    data = {}
    if not os.path.exists(DATA_FULL_PATH):
        return data

    with open(DATA_FULL_PATH, "r") as f:
        data = json.load(f)
    return data

def set_data_hdd(amount: int) -> bool:

    try:
        data = { "amount": amount }
        with open(DATA_FULL_PATH, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(e)
        return False

    return True


def get_side_data(side: str) -> dict:

    result = { "message": "", "position": POS_ERROR, "type": TYPE_ERROR }
    side_detail: List[str] = side.split("/")
    if len(side_detail) == 1:
        result["message"] = side
        return result

    message= "주문: "
    if side_detail[0] == "entry":
        message += "진입"
        result["position"] = POS_ENTRY

    if side_detail[0] == "close":
        message += "청산"
        result["position"] = POS_CLOSE

    if side_detail[1] == "buy":
        message += " / 매수"
        result["type"] = TYPE_LONG

    if side_detail[1] == "sell":
        message += " / 매도"
        result["type"] = TYPE_SHORT

    result["message"] = message
    return result


def save_amount(amount: int, side: dict) -> str:
    """
    주문 가중치 (수량) 를 저장하고, 주문 가중치 (퍼센트) 를 문자열 형태로 반환한다.
    주문 가중치를 저장하지 못했다면, 빈 문자열을 반환한다.
    """

    if side["position"] == POS_ENTRY:
        # 주문타입이 신규 주문이라면 수량을 저장한다.
        stat = set_data_hdd(amount)
        if stat is False:
            return "save error"
        return "3 / 3"

    if side["position"] == POS_CLOSE:
        # 주문타입이 청산 주문이라면 저장된 수량을 가져와 청산 수량 비율을 계산한다.
        data: dict = get_data_hdd()
        if "amount" not in data:
            return "get error (key error)"

        init_amount: int = data.get("amount", -1)
        if init_amount == -1:
            return "get error (init_amount)"
        rate: int = init_amount // 3
        return f"{amount // rate} / 3"



def future_alert_1(msg: dict) -> str:

    if "password" not in msg:
        return str(msg)

    side: str = msg.get("side", "")
    price: str = msg.get("price", "")
    order_name: str = msg.get("order_name", "")

    exchange: str = msg.get("exchange", "")
    quote: str = msg.get("quote", "")

    amount: int = -1
    try:
        amount = int(msg.get("amount", "-1"))
    except Exception as e:
        print(e)

    if amount < 0:
        return str(msg)

    side_data: dict = get_side_data(side)
    percent: str = save_amount(amount, side_data)

    message  = "# 선물 조건식 1 알람\n"
    message += "-------------------------\n"
    message += (side_data["message"] + "\n")
    message += f"주문 종목: {exchange} / {quote}\n"
    message += f"주문 가격: {price}\n"
    message += f"주문 가중치: {percent}  ({amount})\n"
    message += f"주문 설명: {order_name}\n"
    message += "-------------------------\n"

    return message


# {'password': 'rich0122', 'exchange': 'CME_MINI', 'base': '', 'quote': 'NQ1!', 'side': 'close/sell', 'price': '19788.50', 'amount': '22', 'percent': 'NaN', 'margin_mode': '', 'order_name': '롱 종료'}
