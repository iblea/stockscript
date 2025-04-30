import os
import sys
import json


SCRIPT_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE: str = "conf/config.json"
CONFIG_PATH: str = os.path.join(SCRIPT_DIR, CONFIG_FILE)

CERT_FILE: str = "cert/server.crt"
KEY_FILE: str = "cert/server.key"

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

    obj: any = data.get("trade")
    if obj is None or obj == "":
        print("Error: config.json에 trade 설정이 없습니다.")
        return False

    rest_api: any = data.get("rest_api")
    if rest_api is None:
        print("Error: config.json에 rest_api 설정이 없습니다.")
        return False

    use_api: str = rest_api.get("use")
    if use_api is None:
        print("Error: config.json에 rest_api.use 설정이 없습니다.")
        return False
    elif use_api == "kiwoom":
        obj = rest_api.get("kiwoom")
        if obj is None or obj == "":
            print("Error: config.json에 rest_api.kiwoom (키움증권 api) 설정이 없습니다.")
            return False
    elif use_api == "koreainvestment":
        obj = rest_api.get("koreainvestment")
        if obj is None or obj == "":
            print("Error: config.json에 rest_api.koreainvestment (한국투자증권 api) 설정이 없습니다.")
            return False
    else:
        print("Error: rest_api.use 값이 유효하지 않습니다.")
        return False

    flask: any = data.get("flask")
    if flask is None:
        print("Error: config.json에 flask 웹서버 설정이 없습니다.")
        return False

    http_port: any = flask.get("http_port")
    if http_port is None:
        print("Error: config.json에 flask.http_port 설정이 없습니다.")
        return False
    elif http_port < 0 or http_port > 65535:
        print("Error: config.json에 flask.http_port 값이 유효하지 않습니다. 포트 값은 0~65535 사이여야 합니다.")
        return False
    https_port: any = flask.get("https_port")
    if https_port is None:
        print("Error: config.json에 flask.https_port 설정이 없습니다.")
        return False
    elif https_port < 0 or https_port > 65535:
        print("Error: config.json에 flask.https_port 값이 유효하지 않습니다. 포트 값은 0~65535 사이여야 합니다.")
        return False

    if http_port == https_port:
        print("Error: flask.http_port와 flask.https_port는 다른 값이어야 합니다.")
        return False

    return True



def check_cert() -> bool:
    cert_path: str = os.path.join(SCRIPT_DIR, CERT_FILE)
    key_path: str = os.path.join(SCRIPT_DIR, KEY_FILE)

    if not os.path.exists(cert_path):
        print(f"Error: SSL 인증서 파일이 존재하지 않습니다. {CERT_FILE} 파일을 생성해주세요.")
        return False
    if not os.path.exists(key_path):
        print(f"Error: SSL 키 파일이 존재하지 않습니다. {KEY_FILE} 파일을 생성해주세요.")
        return False

    return True


