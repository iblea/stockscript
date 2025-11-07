"""
만트라 밴드 알림 메시지 포맷팅 모듈
"""

from typing import Dict, Any, Optional


def format_mantra_alert(data: Dict[str, Any]) -> str:
    """
    만트라 밴드 알림 메시지를 포맷팅하여 반환

    Args:
        data: TradingView에서 전송된 JSON 데이터

    Returns:
        포맷팅된 디스코드 메시지 문자열
    """
    try:
        # 필수 필드 검증
        if not _validate_data(data):
            return ""

        # alertType에 따른 메시지 헤더 생성
        alert_type = data.get("alertType", 0)
        message = data.get("message", "")

        # 헤더 생성
        header = _get_alert_header(alert_type, message)

        # 현재 가격
        current_price = data.get("price", {}).get("close", 0)

        # MA 데이터 포맷팅
        ma_section = _format_ma_section(data.get("MA", {}))

        # Diff 섹션 포맷팅 (보조지표)
        diff_section = _format_diff_section(data)

        # 최종 메시지 조합
        result = f"""[만트라 밴드 알림]
{header}
Current Price: {_round_value(current_price)}
```
{ma_section}
``````diff
{diff_section}
```
vwap: {_round_value(data.get('MA', {}).get('VWAP', 0))}
adx: {_round_value(data.get('dmi', {}).get('adx', 0))}
atr: {_round_value(data.get('atr', 0))}
Current Price: {_round_value(current_price)}
{header}
"""

        return result

    except Exception as e:
        print(f"Error in format_mantra_alert: {e}")
        return ""


def _validate_data(data: Dict[str, Any]) -> bool:
    """
    필수 데이터 필드 검증
    """
    if data is None:
        return False

    required_fields = ["price", "MA", "rsi", "macd", "dmi"]
    for field in required_fields:
        if field not in data:
            print(f"Missing required field: {field}")
            return False

    return True


def _get_alert_header(alert_type: int, message: str) -> str:
    """
    alertType에 따른 헤더 문자열 생성

    alertType:
        1: 롱 진입
        -1: 숏 진입
        0: 종료 (롱 종료/숏 종료)
    """
    if alert_type == 1:
        return "🟢 롱 진입 🟢"
    elif alert_type == -1:
        return "🔴 숏 진입 🔴"
    elif alert_type == 0:
        # message를 보고 롱 종료인지 숏 종료인지 판단
        if "롱" in message:
            return "🟡 롱 종료 🟡"
        elif "숏" in message:
            return "🟡 숏 종료 🟡"
        else:
            return "🟡 종료 🟡"
    else:
        return "⚪ 알림 ⚪"


def _format_ma_section(ma_data: Dict[str, Any]) -> str:
    """
    MA(이동평균) 데이터 포맷팅
    """
    # 순서대로 출력
    lines = []

    # VWAP을 맨 위에 출력
    lines.append(f"vwap: {_round_value(ma_data.get('VWAP', 0))}")
    lines.append(f"  5: {_round_value(ma_data.get('5', 0))}")
    lines.append(f" 20: {_round_value(ma_data.get('20', 0))}")
    lines.append(f" 60: {_round_value(ma_data.get('60', 0))}")
    lines.append(f"120: {_round_value(ma_data.get('120', 0))}")

    # 5day, 20day (또는 5d, 20d)
    day5 = ma_data.get('5day', ma_data.get('5d', 0))
    day20 = ma_data.get('20day', ma_data.get('20d', 0))

    lines.append(f" 5d: {_round_value(day5)}")
    lines.append(f"20d: {_round_value(day20)}")

    return "\n".join(lines)


def _format_diff_section(data: Dict[str, Any]) -> str:
    """
    Diff 섹션 포맷팅 (보조지표)
    """
    lines = []

    # 1. MACD
    macd_line = _format_macd(data.get("macd", {}))
    lines.append(macd_line)

    # 2. Oscillator
    osc_line = _format_oscillator(data.get("macd", {}))
    lines.append(osc_line)

    # 3. MFI
    mfi_line = _format_mfi(data.get("rsi", {}))
    lines.append(mfi_line)

    # 4. RSI
    rsi_line = _format_rsi(data.get("rsi", {}))
    lines.append(rsi_line)

    # 5. DMI
    dmi_line = _format_dmi(data.get("dmi", {}))
    lines.append(dmi_line)

    # 6. 시/고/저/종
    price_line = _format_price(data.get("price", {}))
    lines.append(price_line)

    return "\n".join(lines)


def _format_macd(macd_data: Dict[str, Any]) -> str:
    """
    MACD 포맷팅
    macd > signal = +, macd < signal = -
    """
    macd_val = macd_data.get("macd", 0)
    signal_val = macd_data.get("signal", 0)

    prefix = ""
    emoji = ""

    if macd_val > signal_val:
        prefix = "+"
        emoji = "🟢"
    elif macd_val < signal_val:
        prefix = "-"
        emoji = "🔴"

    return f"{prefix} {emoji} macd: {_round_value(macd_val)} / {_round_value(signal_val)}  (macd / signal)".strip()


def _format_oscillator(macd_data: Dict[str, Any]) -> str:
    """
    Oscillator 포맷팅
    oscillator > 0 = +, oscillator < 0 = -
    """
    # 필드명이 "osilator" 또는 "oscillator"일 수 있음
    osc_val = macd_data.get("oscillator", macd_data.get("osilator", 0))

    prefix = ""
    emoji = ""

    if osc_val > 0:
        prefix = "+"
        emoji = "🟢"
    elif osc_val < 0:
        prefix = "-"
        emoji = "🔴"

    return f"{prefix} {emoji} osilator: {_round_value(osc_val)}".strip()


def _format_mfi(rsi_data: Dict[str, Any]) -> str:
    """
    MFI 포맷팅
    mfi >= 80 = - (과매수), mfi <= 20 = + (과매도)
    """
    mfi_val = rsi_data.get("mfi", 0)

    prefix = ""

    if mfi_val >= 80:
        prefix = "-"
    elif mfi_val <= 20:
        prefix = "+"

    line = f"mfi: {_round_value(mfi_val)}"

    if prefix:
        return f"{prefix} {line}"
    else:
        return line


def _format_rsi(rsi_data: Dict[str, Any]) -> str:
    """
    RSI 포맷팅
    rsi >= 70 = - (과매수), rsi <= 30 = + (과매도)
    """
    rsi_val = rsi_data.get("rsi", 0)
    signal_val = rsi_data.get("signal", 0)

    prefix = ""
    emoji = ""

    if rsi_val >= 70:
        prefix = "-"
        emoji = "🔴"
    elif rsi_val <= 30:
        prefix = "+"
        emoji = "🟢"

    line = f"rsi: {_round_value(rsi_val)} / {_round_value(signal_val)} (rsi / signal)"

    if prefix and emoji:
        return f"{prefix} {emoji} {line}"
    else:
        return line


def _format_dmi(dmi_data: Dict[str, Any]) -> str:
    """
    DMI 포맷팅
    diplus > diminus = +, diplus < diminus = -
    """
    diplus_val = dmi_data.get("diplus", 0)
    diminus_val = dmi_data.get("diminus", 0)

    prefix = ""
    emoji = ""

    if diplus_val > diminus_val:
        prefix = "+"
        emoji = "🟢"
    elif diplus_val < diminus_val:
        prefix = "-"
        emoji = "🔴"

    return f"{prefix} {emoji} dmi: {_round_value(diplus_val)} / {_round_value(diminus_val)}".strip()


def _format_price(price_data: Dict[str, Any]) -> str:
    """
    시/고/저/종 포맷팅
    (종가 - 시가) > 0 = +, < 0 = -
    """
    open_val = price_data.get("open", 0)
    high_val = price_data.get("high", 0)
    low_val = price_data.get("low", 0)
    close_val = price_data.get("close", 0)

    diff = close_val - open_val

    prefix = ""

    if diff > 0:
        prefix = "+"
    elif diff < 0:
        prefix = "-"

    diff_str = f"({'+' if diff > 0 else ''}{_round_value(diff)})" if diff != 0 else "(0)"

    line = f"시/고/저/종: {_round_value(open_val)} / {_round_value(high_val)} / {_round_value(low_val)} / {_round_value(close_val)} {diff_str}"

    if prefix:
        return f"{prefix} {line}"
    else:
        return line


def _round_value(value: float) -> str:
    """
    소숫점 2자리로 반올림하여 문자열 반환
    """
    return f"{value:.2f}"
