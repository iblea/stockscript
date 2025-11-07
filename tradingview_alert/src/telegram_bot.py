import telegram
import asyncio
import threading
from time import sleep
from telegram.ext import Application, CommandHandler, MessageHandler, filters

import msg
import alert_manager
from toggle_settings import toggle_settings

tg_bot: any = None
tg_chatid: any = None
tg_lock = threading.Lock()
tg_alert_repeat: int = 1
tg_application = None
tg_stop_event = threading.Event()  # 종료 이벤트

# bot will not be able to send more than 20 messages per minute to the same group.
# telegram은 분당 20 req 이상의 요청을 보낼 수 없다.
# 또한 초당 두개 이상의 메시지를 보낼 수 없다. (이러한 burst 형식의 메시지를 보낼 시 429 오류 발생)
# https://api.telegram.org/bot{TOKEN}/getUpdates -> chat id 의 내용이 채널
async def telegram_msg_send(msg_str):
    global tg_bot
    global tg_chatid
    global tg_alert_repeat

    if tg_bot is None:
        return
    if tg_chatid < 0:
        return

    if msg_str == "":
        return

    # Application 객체인 경우 bot 속성 사용
    if hasattr(tg_bot, 'bot'):
        await tg_bot.bot.send_message(chat_id=tg_chatid, text=msg_str)
    else:
        await tg_bot.sendMessage(chat_id=tg_chatid, text=msg_str)

# 텔레그램 명령어 핸들러
async def handle_chk_command(update, context):
    # chk 명령 처리
    msg.safe_string.set_value("")
    await update.message.reply_text("alert check")


async def handle_chka_command(update, context):
    # chka 명령 처리
    message = alert_manager.clear_triggered_alerts()
    await update.message.reply_text(message)

# async def handle_message(update, context):
#     # 메시지 처리
#     message_text = update.message.text.lower()
#
#     # "chk" 메시지 확인
#     if message_text == "chk":
#         await update.message.reply_text("ok")

def telegram_bot_thread():
    """텔레그램 봇 폴링과 메시지 전송을 모두 처리하는 통합 스레드"""
    global tg_bot, tg_stop_event

    # 새 이벤트 루프 생성 및 설정
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # 비동기 함수로 모든 작업 처리
    async def run_bot():
        # 봇 초기화 및 시작
        await tg_bot.initialize()
        await tg_bot.updater.start_polling(allowed_updates=["message"])
        await tg_bot.start()

        print("텔레그램 봇 준비 완료")

        # 메시지 전송 작업
        last_check_time = 0

        # 종료 신호가 올 때까지 실행
        while not tg_stop_event.is_set():
            # alert 확인
            alert_manager.check_alerts()

            # 현재 시간
            current_time = asyncio.get_event_loop().time()

            # tg_alert_repeat 간격으로 메시지 확인 및 전송
            if current_time - last_check_time >= tg_alert_repeat:
                last_check_time = current_time

                # 전송할 메시지 확인
                msgdata = msg.safe_string.get_value()

                # mantra_string에서 메시지 읽기
                mantra_message = msg.mantra_string.get_value()

                # adi_string에서 메시지 읽기
                adi_message = msg.adi_string.get_value()

                # alert 메시지 추가
                alert_message = alert_manager.get_alert_message()
                if alert_message:
                    if msgdata:
                        msgdata += "\n" + alert_message
                    else:
                        msgdata = alert_message

                # mantra_message를 메시지에 추가 (토글 설정 확인)
                if toggle_settings.is_mantra_alert_enabled():
                    if mantra_message:
                        if msgdata:
                            msgdata += "\n" + mantra_message
                        else:
                            msgdata = mantra_message

                    # adi_message를 메시지에 추가
                    if adi_message:
                        if msgdata:
                            msgdata += "\n" + adi_message
                        else:
                            msgdata = adi_message

                if msgdata and msgdata != "":
                    await telegram_msg_send(msgdata)

                # 전송 후 mantra_string과 adi_string 초기화 (한 번만 전송)
                msg.mantra_string.set_value("")
                msg.adi_string.set_value("")

            # 짧은 대기 (CPU 부하 방지)
            await asyncio.sleep(1)

        # 종료 처리
        # await telegram_msg_send("텔레그램 봇이 종료됩니다")
        await tg_bot.updater.stop()
        await tg_bot.stop()
        await tg_bot.shutdown()
        print("텔레그램 봇 종료 완료")

    # 최소한의 예외 처리만 유지
    try:
        loop.run_until_complete(run_bot())
    except Exception as e:
        print(f"텔레그램 봇 오류: {e}")
    finally:
        loop.close()


def start_telegram_bot(config: dict):
    global tg_bot
    global tg_chatid
    global tg_alert_repeat
    global tg_stop_event

    # 종료 이벤트 초기화
    tg_stop_event.clear()

    bot_use = config["bot"]["use_telegram"]

    if bot_use is False:
        print("telegram bot is not used")
        return

    telegram_conf: dict = config.get("telegram", None)
    if telegram_conf is None:
        print("telegram bot token is None")
        return

    token = telegram_conf.get("token")
    tg_chatid = telegram_conf.get("chat_id")
    tg_alert_repeat = telegram_conf.get("alert_interval")

    # 봇 애플리케이션 생성
    tg_bot = Application.builder().token(token).build()

    # 명령어 처리기 등록
    tg_bot.add_handler(CommandHandler("chk", handle_chk_command))
    tg_bot.add_handler(CommandHandler("chka", handle_chka_command))

    print("텔레그램 봇을 시작합니다")

    # 통합 봇 스레드 시작
    bot_thread = threading.Thread(target=telegram_bot_thread)
    bot_thread.daemon = True
    bot_thread.start()


def telegram_bot_shutdown():
    """텔레그램 봇을 안전하게 종료하는 함수"""
    global tg_stop_event

    print("텔레그램 봇 종료 신호 전송")
    tg_stop_event.set()

    # 종료 처리를 위한 대기 시간
    sleep(2)

    print("텔레그램 봇 종료 완료")




