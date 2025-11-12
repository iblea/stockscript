"""
국면 변경 알림 메시지 포맷팅 모듈
"""

from typing import Dict, Any, Optional


def format_phase_alert(data: Dict[str, Any]) -> str:
    """
    국면 변경 알림 메시지를 포맷팅하여 반환

    Args:
        data: TradingView에서 전송된 JSON 데이터

    Returns:
        포맷팅된 디스코드 메시지 문자열
    """
    try:
        # 필수 필드 검증
        if not _validate_phase_data(data):
            return ""

        # 헤더 생성 (국면 변경 + 진입/종료 플래그)
        header = _get_phase_alert_header(data)

        # Phase 라인 생성
        phase_line = _get_phase_line(data)

        # BB (Band Breath) 값
        bb_val = data.get("bb", 0)

        # MA 데이터 포맷팅 (값이 높은 순서대로)
        ma_section = _format_phase_ma_section(data.get("MA", {}))

        # MACD 섹션 포맷팅 (MA 순서와 동일하게)
        macd_section = _format_phase_macd_section(data)

        # Diff 섹션 포맷팅 (보조지표)
        diff_section = _format_phase_diff_section(data)

        # 최종 메시지 조합
        vwap_val = data.get('MA', {}).get('VWAP') or 0
        atr_val = data.get('atr') or 0
        current_price = data.get("price", {}).get("close") or 0

        result = f"""# {header}
{phase_line}
BB: {_round_value(bb_val)}
```
    BB: {_round_value(bb_val)}
{ma_section}
``````diff
BB: {_round_value(bb_val)}
{macd_section}
``````diff
{diff_section}
```
vwap: {_round_value(vwap_val)}
BB: {_round_value(bb_val)}
{phase_line}
atr: {_round_value(atr_val)}
Current Price: {_round_value(current_price)}
{header}
"""

        return result

    except Exception as e:
        print(f"Error in format_phase_alert: {e}")
        import traceback
        traceback.print_exc()
        return ""


def _validate_phase_data(data: Dict[str, Any]) -> bool:
    """
    국면 변경 데이터 필수 필드 검증
    """
    if data is None:
        return False

    required_fields = ["price", "MA", "rsi", "dmi", "macd_short", "macd_middle", "macd_long"]
    for field in required_fields:
        if field not in data:
            print(f"Missing required field: {field}")
            return False

    return True


def _get_phase_alert_header(data: Dict[str, Any]) -> str:
    """
    국면 변경 헤더 생성
    phaseflag(국면 변경)와 mantraflag(진입/종료)를 조합하여 헤더 생성

    예시:
    - 🟢 (MA) 롱 진입 🟢
    - 🔴 (CD) 숏 진입 🔴
    - 🟡 (MA/CD) 숏 종료 🟡
    - (MA)
    """
    phaseflag = data.get("phaseflag", 0)
    mantraflag = data.get("mantraflag", 0)  # 진입/종료 플래그

    # Phase flag 텍스트 생성
    phase_text = ""
    if phaseflag == 1:
        phase_text = "(MA)"
    elif phaseflag == 2:
        phase_text = "(CD)"
    elif phaseflag == 3:
        phase_text = "(MA/CD)"

    # 진입/종료 플래그 텍스트 생성
    flag_text = ""
    emoji = ""
    if mantraflag == 1:
        flag_text = "롱 진입"
        emoji = "🟢"
    elif mantraflag == 2:
        flag_text = "숏 진입"
        emoji = "🔴"
    elif mantraflag == -1:
        flag_text = "롱 종료"
        emoji = "🟡"
    elif mantraflag == -2:
        flag_text = "숏 종료"
        emoji = "🟡"

    # 조합
    if phaseflag > 0 and mantraflag != 0:
        # 둘 다 있을 때: 🟢 (MA) 롱 진입 🟢
        return f"{emoji} {phase_text} {flag_text} {emoji}"
    elif phaseflag > 0:
        # phase만 있을 때: (MA)
        return f"{phase_text}"
    elif mantraflag != 0:
        # 진입/종료만 있을 때: 🟢 롱 진입 🟢
        return f"{emoji} {flag_text} {emoji}"
    else:
        # 둘 다 없을 때
        return "⚪ 알림 ⚪"


def _get_phase_line(data: Dict[str, Any]) -> str:
    """
    Phase 라인 생성

    예시:
    - 🟢 Phase: 1 / 2 🟢
    - 🔴 Phase: 4 / 4 🔴
    - 🟢 Phase: 0>1 / 4 🔴
    - 🔴 Phase: 5>4 / 2>4 🔴
    """
    phaseflag = data.get("phaseflag", 0)
    phase = data.get("phase", 0)
    macdphase = data.get("macdphase", 0)
    prevphase = data.get("prevphase", 0)
    prevmacdphase = data.get("prevmacdphase", 0)

    # MA phase 텍스트 생성
    if phaseflag > 0 and prevphase != phase:
        ma_phase_text = f"{prevphase}>{phase}"
    else:
        ma_phase_text = f"{phase}"

    # MACD phase 텍스트 생성
    if phaseflag > 0 and prevmacdphase != macdphase:
        macd_phase_text = f"{prevmacdphase}>{macdphase}"
    else:
        macd_phase_text = f"{macdphase}"

    # 앞 emoji 결정 (현재 MA phase 기준)
    front_emoji = "🟢" if phase in [0, 1, 2] else "🔴"

    # 뒤 emoji 결정 (현재 MACD phase 기준)
    back_emoji = "🟢" if macdphase in [0, 1, 2] else "🔴"

    return f"{front_emoji} Phase: {ma_phase_text} / {macd_phase_text} {back_emoji}"


def _format_phase_ma_section(ma_data: Dict[str, Any]) -> str:
    """
    Phase Alert용 MA 섹션 포맷팅
    값이 높은 순서대로 출력
    """
    short_val = ma_data.get("short") or 0
    middle_val = ma_data.get("middle") or 0
    long_val = ma_data.get("long") or 0

    # (값, 이름, 우선순위) 튜플 리스트 생성
    # 값이 같을 경우 short, middle, long 순서로 출력하기 위해 우선순위 부여
    ma_list = [
        (short_val, "short", 0),
        (middle_val, "middle", 1),
        (long_val, "long", 2),
    ]

    # 값이 높은 순서대로 정렬 (값이 같으면 우선순위 순서)
    ma_list.sort(key=lambda x: (-x[0], x[2]))

    lines = []
    for val, name, _ in ma_list:
        lines.append(f"{name:>6}: {_round_value(val)}")

    return "\n".join(lines)


def _format_phase_macd_section(data: Dict[str, Any]) -> str:
    """
    Phase Alert용 MACD 섹션 포맷팅
    MA와 동일한 순서로 출력
    """
    ma_data = data.get("MA", {})
    short_val = ma_data.get("short") or 0
    middle_val = ma_data.get("middle") or 0
    long_val = ma_data.get("long") or 0

    # MA와 동일한 순서 계산
    ma_list = [
        (short_val, "short", 0, data.get("macd_short", {})),
        (middle_val, "middle", 1, data.get("macd_middle", {})),
        (long_val, "long", 2, data.get("macd_long", {})),
    ]
    ma_list.sort(key=lambda x: (-x[0], x[2]))

    lines = []
    for _, name, _, macd_data in ma_list:
        macd_val = macd_data.get("macd") or 0
        signal_val = macd_data.get("signal") or 0
        oscillator_val = macd_data.get("oscillator") or 0

        # macd > signal이면 +, macd < signal이면 -
        prefix = ""
        emoji = ""
        if macd_val > signal_val:
            prefix = "+"
            emoji = "🟢"
        elif macd_val < signal_val:
            prefix = "-"
            emoji = "🔴"

        line = f"{prefix} {emoji} {name:>6}: {_round_value(macd_val)} / {_round_value(signal_val)} ({_round_value(oscillator_val)})".strip()
        lines.append(line)

    return "\n".join(lines)


def _format_phase_diff_section(data: Dict[str, Any]) -> str:
    """
    Phase Alert용 Diff 섹션 포맷팅 (보조지표)
    """
    lines = []

    # 1. MFI
    mfi_line = _format_phase_mfi(data.get("rsi", {}))
    lines.append(mfi_line)

    # 2. RSI
    rsi_line = _format_phase_rsi(data.get("rsi", {}))
    lines.append(rsi_line)

    # 3. DMI
    dmi_line = _format_phase_dmi(data.get("dmi", {}))
    lines.append(dmi_line)

    # 4. 시/고/저/종
    price_line = _format_phase_price(data.get("price", {}))
    lines.append(price_line)

    return "\n".join(lines)


def _format_phase_mfi(rsi_data: Dict[str, Any]) -> str:
    """
    Phase Alert용 MFI 포맷팅
    mfi >= 80 = - (과매수), mfi <= 20 = + (과매도)
    """
    mfi_val = rsi_data.get("mfi") or 0

    line = f"mfi: {_round_value(mfi_val)}"
    return line


def _format_phase_rsi(rsi_data: Dict[str, Any]) -> str:
    """
    Phase Alert용 RSI 포맷팅
    rsi >= 70 = - (과매수), rsi <= 30 = + (과매도)
    """
    rsi_val = rsi_data.get("rsi") or 0
    signal_val = rsi_data.get("signal") or 0

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


def _format_phase_dmi(dmi_data: Dict[str, Any]) -> str:
    """
    Phase Alert용 DMI 포맷팅
    diplus > diminus = +, diplus < diminus = -
    """
    diplus_val = dmi_data.get("diplus") or 0
    diminus_val = dmi_data.get("diminus") or 0
    adi_val = dmi_data.get("adi") or 0

    prefix = ""
    emoji = ""

    if diplus_val > diminus_val:
        prefix = "+"
        emoji = "🟢"
    elif diplus_val < diminus_val:
        prefix = "-"
        emoji = "🔴"

    return f"{prefix} {emoji} dmi: {_round_value(diplus_val)} / {_round_value(diminus_val)} ({_round_value(adi_val)})".strip()


def _format_phase_price(price_data: Dict[str, Any]) -> str:
    """
    Phase Alert용 시/고/저/종 포맷팅
    (종가 - 시가) > 0 = +, < 0 = -
    """
    open_val = price_data.get("open") or 0
    high_val = price_data.get("high") or 0
    low_val = price_data.get("low") or 0
    close_val = price_data.get("close") or 0

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


def _round_value(value: Optional[float]) -> str:
    """
    소숫점 2자리로 반올림하여 문자열 반환
    None이나 null 값은 0으로 처리
    """
    if value is None:
        return "0.00"
    return f"{value:.2f}"
