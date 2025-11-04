import json
from os.path import exists
from config import DATA_DIR
import stock_data

ALERT_DATA_PATH = DATA_DIR + "alert.json"

# 메모리에 저장된 alert 데이터
alert_data: dict = {}

# 알람이 발생한 티커 목록 (도달한 alert)
triggered_alerts: set = set()


def validate_price(price_str: str) -> tuple[bool, float | None, str]:
    """
    가격 문자열 검증
    Returns: (유효성, 변환된 float 값 또는 None, 에러 메시지)
    """
    # '-' 인 경우 무시
    if price_str == "-":
        return True, None, ""

    # 숫자로 변환 시도
    try:
        price = float(price_str)
        return True, price, ""
    except ValueError:
        return False, None, "가격은 숫자 또는 '-'로 입력해야 합니다"


def set_alert(ticker: str, target_price_str: str, stop_loss_str: str) -> tuple[bool, str]:
    """
    alert 설정
    Returns: (성공 여부, 메시지)
    """
    global alert_data

    # 티커를 소문자로 변환
    ticker = ticker.lower()

    # 티커가 stock_data에 있는지 확인
    if ticker not in stock_data.stock_data_dict:
        return False, f"티커 '{ticker}'를 찾을 수 없습니다. stock_data에 등록된 티커를 사용해주세요."

    # 목표가 검증
    valid, target_price, error_msg = validate_price(target_price_str)
    if not valid:
        return False, f"목표가 오류: {error_msg}"

    # 손절가 검증
    valid, stop_loss, error_msg = validate_price(stop_loss_str)
    if not valid:
        return False, f"손절가 오류: {error_msg}"

    # 둘 다 None이면 안됨
    if target_price is None and stop_loss is None:
        return False, "목표가와 손절가를 모두 '-'로 설정할 수 없습니다"

    # alert 데이터 저장
    alert_data[ticker] = {
        "target_price": target_price,
        "stop_loss_price": stop_loss
    }

    # 파일에 저장
    save_alert_to_disk()

    # 성공 메시지 생성
    msg = f"알람 설정 완료: {ticker.upper()}\n"
    if target_price is not None:
        msg += f"  목표가: {target_price}\n"
    if stop_loss is not None:
        msg += f"  손절가: {stop_loss}\n"

    return True, msg


def check_alerts() -> list[str]:
    """
    모든 alert를 확인하고 도달한 alert 목록 반환
    Returns: 도달한 티커 목록
    """
    global alert_data, triggered_alerts

    reached_alerts = []

    for ticker, alert_info in alert_data.items():
        # 티커의 현재 가격 가져오기
        if ticker not in stock_data.stock_data_dict:
            continue

        current_price = stock_data.stock_data_dict[ticker].getPrice()
        target_price = alert_info.get("target_price")
        stop_loss_price = alert_info.get("stop_loss_price")

        # 목표가 도달 확인
        if target_price is not None and current_price >= target_price:
            reached_alerts.append(ticker)
            triggered_alerts.add(ticker)
            continue

        # 손절가 도달 확인
        if stop_loss_price is not None and current_price <= stop_loss_price:
            reached_alerts.append(ticker)
            triggered_alerts.add(ticker)
            continue

    return reached_alerts


def get_alert_message() -> str:
    """
    도달한 alert 메시지 생성
    """
    global triggered_alerts

    if not triggered_alerts:
        return ""

    msg = "🚨 가격 알람 발생! 🚨\n\n"

    for ticker in triggered_alerts:
        if ticker not in stock_data.stock_data_dict:
            continue

        stock = stock_data.stock_data_dict[ticker]
        alert_info = alert_data.get(ticker)

        if alert_info is None:
            continue

        current_price = stock.getPrice()
        target_price = alert_info.get("target_price")
        stop_loss_price = alert_info.get("stop_loss_price")

        msg += f"티커: {ticker.upper()}\n"
        msg += f"현재가: {current_price}\n"

        if target_price is not None and current_price >= target_price:
            msg += f"✅ 목표가 도달: {target_price}\n"

        if stop_loss_price is not None and current_price <= stop_loss_price:
            msg += f"⛔ 손절가 도달: {stop_loss_price}\n"

        msg += "\n"

    return msg


def clear_triggered_alerts() -> str:
    """
    도달한 alert 삭제 (/chka 명령어)
    Returns: 삭제된 티커 목록 메시지
    """
    global alert_data, triggered_alerts

    if not triggered_alerts:
        return "도달한 알람이 없습니다"

    deleted_tickers = list(triggered_alerts)

    # alert_data에서 삭제
    for ticker in deleted_tickers:
        if ticker in alert_data:
            del alert_data[ticker]

    # triggered_alerts 초기화
    triggered_alerts.clear()

    # 파일에 저장
    save_alert_to_disk()

    msg = f"다음 티커의 알람이 삭제되었습니다: {', '.join([t.upper() for t in deleted_tickers])}"
    return msg


def delete_alert(ticker: str) -> tuple[bool, str]:
    """
    특정 티커의 alert 삭제 (/adel 명령어)
    Returns: (성공 여부, 메시지)
    """
    global alert_data, triggered_alerts

    ticker = ticker.lower()

    if ticker not in alert_data:
        return False, f"티커 '{ticker.upper()}'의 알람이 설정되어 있지 않습니다"

    # alert_data에서 삭제
    del alert_data[ticker]

    # triggered_alerts에서도 삭제 (있다면)
    if ticker in triggered_alerts:
        triggered_alerts.remove(ticker)

    # 파일에 저장
    save_alert_to_disk()

    return True, f"티커 '{ticker.upper()}'의 알람이 삭제되었습니다"


def save_alert_to_disk() -> None:
    """alert 데이터를 파일에 저장"""
    global alert_data

    json_string = json.dumps(alert_data, indent=4)

    with open(ALERT_DATA_PATH, 'w') as f:
        f.write(json_string)


def load_alert_from_disk() -> bool:
    """파일에서 alert 데이터 로드"""
    global alert_data

    if not exists(ALERT_DATA_PATH):
        print(f"Alert file not found: {ALERT_DATA_PATH}")
        # 파일이 없으면 빈 딕셔너리로 초기화하고 파일 생성
        alert_data = {}
        save_alert_to_disk()
        return True

    try:
        with open(ALERT_DATA_PATH, 'r') as f:
            alert_data = json.load(f)
        return True
    except Exception as e:
        print(f"Error loading alert data: {e}")
        return False
