import os
import sys
import json


SCRIPT_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR: str   = SCRIPT_DIR + "/data/"

CONFIG_FILE: str = "/conf/config.json"
CONFIG_PATH: str = SCRIPT_DIR + CONFIG_FILE

# CONFIG_FILE: str = "conf/config.json"
# CONFIG_PATH: str = os.path.join(SCRIPT_DIR, CONFIG_FILE)

HTTPS_CERT_FILE: str = "cert/server.crt"
HTTPS_KEY_FILE: str = "cert/server.key"

HTTPS_CERT_PATH: str = os.path.join(SCRIPT_DIR, HTTPS_CERT_FILE)
HTTPS_KEY_PATH: str = os.path.join(SCRIPT_DIR, HTTPS_KEY_FILE)



data: dict = None

def exist_config() -> None:
    global data
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: '{CONFIG_PATH}' 파일을 찾을 수 없습니다.")
        print(f"conf/config_sample.json 파일을 복사하여 {CONFIG_FILE} 파일을 생성해주세요.")
        print("커맨드는 다음과 같습니다:")
        print(f"cp conf/config_sample.json {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)

    if check_config() is False:
        print("Error: 설정 파일이 유효하지 않아 프로그램을 종료합니다.")
        sys.exit(1)

def check_config() -> bool:
    global data
    if data is None:
        return False

    obj: any = data.get("trade", None)
    if obj is None or obj == "":
        print("Error: config.json에 trade 설정이 없습니다.")
        return False

    rest_api: any = data.get("rest_api", None)
    if rest_api is None:
        print("Error: config.json에 rest_api 설정이 없습니다.")
        return False

    use_api: str = rest_api.get("use", None)
    if use_api is None:
        print("Error: config.json에 rest_api.use 설정이 없습니다.")
        return False
    elif use_api == "kiwoom":
        obj = rest_api.get("kiwoom", None)
        if obj is None or obj == "":
            print("Error: config.json에 rest_api.kiwoom (키움증권 api) 설정이 없습니다.")
            return False
    elif use_api == "koreainvestment":
        obj = rest_api.get("koreainvestment", None)
        if obj is None or obj == "":
            print("Error: config.json에 rest_api.koreainvestment (한국투자증권 api) 설정이 없습니다.")
            return False
    else:
        print("Error: rest_api.use 값이 유효하지 않습니다.")
        return False

    flask: any = data.get("flask", None)
    if flask is None:
        print("Error: config.json에 flask 웹서버 설정이 없습니다.")
        return False

    http_port: any = flask.get("http_port", None)
    if http_port is None:
        print("Error: config.json에 flask.http_port 설정이 없습니다.")
        return False
    elif http_port < 0 or http_port > 65535:
        print("Error: config.json에 flask.http_port 값이 유효하지 않습니다. 포트 값은 0~65535 사이여야 합니다.")
        return False
    https_port: any = flask.get("https_port", None)
    if https_port is None:
        print("Error: config.json에 flask.https_port 설정이 없습니다.")
        return False
    elif https_port < 0 or https_port > 65535:
        print("Error: config.json에 flask.https_port 값이 유효하지 않습니다. 포트 값은 0~65535 사이여야 합니다.")
        return False

    if http_port == https_port:
        print("Error: flask.http_port와 flask.https_port는 다른 값이어야 합니다.")
        return False

    bot_data = data.get("bot", None)
    if bot_data is None:
        print("Error: config.json에 bot 설정이 없습니다.")
        return False

    obj = bot_data.get("use_discord", None)
    if obj is None:
        print("Error: config.json에 bot.use_discord 설정이 없습니다.")
        return False

    obj = bot_data.get("use_telegram", None)
    if obj is None:
        print("Error: config.json에 bot.use_telegram 설정이 없습니다.")
        return False

    discord_data = data.get("discord", None)
    if discord_data is None:
        print("Error: config.json에 discord 설정이 없습니다.")
        return False

    obj = discord_data.get("token", None)
    if obj is None:
        print("Error: config.json에 bot.discord.token 설정이 없습니다.")
        return False

    obj = discord_data.get("server_id", 0)
    if obj == 0:
        print("Error: config.json에 bot.discord.server_id 설정이 없습니다.")
        return False

    obj = discord_data.get("channel_id", 0)
    if obj == 0:
        print("Error: config.json에 bot.discord.channel_id 설정이 없습니다.")
        return False

    obj = discord_data.get("alert_interval", None)
    if obj is None:
        print("Error: config.json에 bot.discord.alert_interval 설정이 없습니다.")
        return False

    telegram_data = data.get("telegram", None)
    if telegram_data is None:
        print("Error: config.json에 telegram 설정이 없습니다.")
        return False

    obj = telegram_data.get("token", None)
    if obj is None:
        print("Error: config.json에 bot.telegram.token 설정이 없습니다.")
        return False

    obj = telegram_data.get("chat_id", 0)
    if obj == 0:
        print("Error: config.json에 bot.telegram.chat_id 설정이 없습니다.")
        return False

    obj = telegram_data.get("alert_interval", None)
    if obj is None:
        print("Error: config.json에 bot.telegram.alert_interval 설정이 없습니다.")
        return False

    return True

def check_cert() -> bool:
    if not os.path.exists(HTTPS_CERT_PATH):
        print(f"Error: SSL 인증서 파일이 존재하지 않습니다. {HTTPS_CERT_FILE} 파일을 생성해주세요.")
        return False
    if not os.path.exists(HTTPS_KEY_PATH):
        print(f"Error: SSL 키 파일이 존재하지 않습니다. {HTTPS_KEY_FILE} 파일을 생성해주세요.")
        return False

    return True


