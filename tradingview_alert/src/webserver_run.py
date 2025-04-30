
import os
import threading
from werkzeug.serving import make_server, WSGIRequestHandler
import webserver_flask as flask_app

from config import check_cert, HTTPS_CERT_PATH, HTTPS_KEY_PATH


# HTTP/1.1 사용하도록 설정
WSGIRequestHandler.protocol_version = "HTTP/1.1"


def run_http(port) -> None:
    http_server = make_server('0.0.0.0', port, flask_app.app)
    http_server.serve_forever()


def check_https() -> bool:

    return False

def run_https(port) -> None:
    https_server = make_server('0.0.0.0', port, flask_app.app, ssl_context=(HTTPS_CERT_PATH, HTTPS_KEY_PATH))
    https_server.serve_forever()


def run_webserver_thread(http_port: int = 8842, https_port: int = 8843) -> None:

    if http_port == 0 and https_port == 0:
        print("web server가 실행되지 않습니다.")
        return

    if http_port == 0:
        print("HTTP 서버가 실행되지 않습니다.")
    else:
        # HTTP 서버 스레드 시작
        http_thread = threading.Thread(target=run_http, args=(http_port,))
        http_thread.daemon = True
        http_thread.start()
        print(f"HTTP 서버가 http://localhost:{http_port} 에서 실행 중입니다.")


    if https_port == 0:
        print("HTTPS 서버가 실행되지 않습니다.")
    else:
        if check_cert() is False:
            print("인증서가 없어 HTTPS 서버가 실행되지 않습니다.")
        else:
            # HTTPS 서버 스레드 시작
            https_thread = threading.Thread(target=run_https, args=(https_port,))
            https_thread.daemon = True
            https_thread.start()
            print(f"HTTPS 서버가 https://localhost:{https_port} 에서 실행 중입니다.")

