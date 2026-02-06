
import os
import time
import threading
import traceback
import waitress
from werkzeug.serving import make_server, WSGIRequestHandler
import webserver_flask as flask_app

from config import check_cert, HTTPS_CERT_PATH, HTTPS_KEY_PATH


# HTTP/1.1 사용하도록 설정 (HTTPS용 werkzeug)
WSGIRequestHandler.protocol_version = "HTTP/1.1"

# 스레드 참조 (외부 모니터링용)
http_thread: threading.Thread | None = None
https_thread: threading.Thread | None = None


def run_http(port) -> None:
    retry_count = 0
    while True:
        try:
            print(f"HTTP 서버 시작 - waitress (재시도: {retry_count})")
            retry_count = 0
            waitress.serve(flask_app.app, host='0.0.0.0', port=port)
            break
        except Exception as e:
            retry_count += 1
            delay = min(2 ** retry_count, 60)
            print(f"HTTP 서버 오류 (재시도 {retry_count}회): {e}")
            traceback.print_exc()
            print(f"{delay}초 후 재시작...")
            time.sleep(delay)


def check_https() -> bool:

    return False

def run_https(port) -> None:
    retry_count = 0
    while True:
        try:
            https_server = make_server('0.0.0.0', port, flask_app.app, ssl_context=(HTTPS_CERT_PATH, HTTPS_KEY_PATH))
            print(f"HTTPS 서버 시작 (재시도: {retry_count})")
            retry_count = 0
            https_server.serve_forever()
            break
        except Exception as e:
            retry_count += 1
            delay = min(2 ** retry_count, 60)
            print(f"HTTPS 서버 오류 (재시도 {retry_count}회): {e}")
            traceback.print_exc()
            print(f"{delay}초 후 재시작...")
            time.sleep(delay)


def is_http_alive() -> bool:
    return http_thread is not None and http_thread.is_alive()

def is_https_alive() -> bool:
    return https_thread is not None and https_thread.is_alive()


def run_webserver_thread(http_port: int = 8842, https_port: int = 8843) -> None:
    global http_thread, https_thread

    if http_port == 0 and https_port == 0:
        print("web server가 실행되지 않습니다.")
        return

    if http_port == 0:
        print("HTTP 서버가 실행되지 않습니다.")
    else:
        if is_http_alive():
            print("HTTP 서버 스레드가 이미 실행 중입니다.")
        else:
            # HTTP 서버 스레드 시작
            http_thread = threading.Thread(target=run_http, args=(http_port,), name="http-server")
            http_thread.daemon = True
            http_thread.start()
            print(f"HTTP 서버가 http://0.0.0.0:{http_port} 에서 실행 중입니다.")

    if https_port == 0:
        print("HTTPS 서버가 실행되지 않습니다.")
    else:
        if check_cert() is False:
            print("인증서가 없어 HTTPS 서버가 실행되지 않습니다.")
        elif is_https_alive():
            print("HTTPS 서버 스레드가 이미 실행 중입니다.")
        else:
            # HTTPS 서버 스레드 시작
            https_thread = threading.Thread(target=run_https, args=(https_port,), name="https-server")
            https_thread.daemon = True
            https_thread.start()
            print(f"HTTPS 서버가 https://0.0.0.0:{https_port} 에서 실행 중입니다.")

