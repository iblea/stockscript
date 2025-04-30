import telegram
import asyncio
import threading
from time import sleep


import msg

tg_bot: any = None
tg_chatid: any = None
tg_lock = threading.Lock()
tg_alert_repeat: int = 1

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

    await tg_bot.sendMessage(chat_id=tg_chatid, text=msg_str)


def telegram_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        # WARNING: sleep 1초시 초당 1회 요청이라 429 too many requests 로 차단될 가능성 있음.
        sleep(tg_alert_repeat)

        msgdata = msg.safe_string.get_value()
        if msgdata is None or msgdata == "":
            continue

        # 초당 2번 이상 메시지를 날리면 오류 난다.
        loop.run_until_complete(telegram_msg_send(msgdata))

    # 사실상 죽은 코드
    loop.close()

def start_telegram_bot(config: dict):
    global tg_bot
    global tg_chatid
    global tg_alert_repeat

    bot_use = config["bot"]["use_telegram"]

    if bot_use is False:
        print("telegram bot is not used")
        return

    telegram_conf: dict = config.get("telegram", None)
    if telegram_conf is None:
        print("telegram bot token is None")
        return

    tg_bot = telegram.Bot(token=telegram_conf.get("token"))
    tg_chatid = telegram_conf.get("chat_id")
    tg_alert_repeat = telegram_conf.get("alert_interval")

    print("텔레그램 봇을 시작합니다")

    tg_thread = threading.Thread(target=telegram_thread)
    tg_thread.daemon = True
    tg_thread.start()




