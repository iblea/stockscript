#!/usr/bin/env python3

import config
import webserver_run as webserver
import signal
import sys
import argparse
import os

from discord_bot import discord_bot_run, discord_bot_shutdown
from telegram_bot import start_telegram_bot

# pip install python-daemon
import daemon
import daemon.pidfile



# 명령행 인자 파싱
parser = argparse.ArgumentParser(description='트레이딩뷰 알림 서버')
parser.add_argument('--daemon', action='store_true', help='데몬으로 실행')
parser.add_argument('--pidfile', type=str, default='/tmp/tradingview_alert.pid', help='PID 파일 경로')
parser.add_argument('--logfile', type=str, default='/tmp/tradingview_alert.log', help='로그 파일 경로')
args = parser.parse_args()

# 종료 플래그
running = True

# 시그널 핸들러 함수
def signal_handler(sig, frame):
    global running
    print("종료 시그널을 받았습니다. 안전하게 종료합니다...")
    running = False

# 종료 시그널 핸들러 등록
signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # kill 명령어

def main():
    config.exist_config()

    flask_config = config.data.get("flask")

    webserver.run_webserver_thread(
        http_port=flask_config.get("http_port", 0),
        https_port=flask_config.get("https_port", 0)
    )

    discord_bot_run(config.data)

    start_telegram_bot(config.data)

    # 시그널 발생 전까지 대기
    signal.pause()

    # 안전한 종료 수행
    discord_bot_shutdown()
    # 웹서버 종료 코드가 필요하다면 여기에 추가

    print("shutdown done")



if __name__ == "__main__":
    if args.daemon:
        print(f"데몬으로 실행 중... (PID 파일: {args.pidfile}, 로그 파일: {args.logfile})")

        # 로그 파일 설정
        log_file = open(args.logfile, 'w+')

        # 데몬 컨텍스트 설정
        context = daemon.DaemonContext(
            working_directory=os.getcwd(),
            umask=0o002,
            pidfile=daemon.pidfile.PIDLockFile(args.pidfile),
            stdout=log_file,
            stderr=log_file,
            # 기본 파일 핸들러 보존
            files_preserve=[log_file],
            # 데몬 모드에서도 표준 입력 유지 (SSL이 종종 필요로 함)
            stdin=sys.stdin,
            # 자식 프로세스로 분리 후 부모 프로세스 종료
            detach_process=True,
        )

        # 시그널 핸들러 설정
        context.signal_map = {
            signal.SIGTERM: signal_handler,
            signal.SIGINT: signal_handler,
        }

        # 데몬으로 실행
        with context:
            # 데몬 모드에서 Discord 연결 전 약간의 지연 시간 추가
            import time
            time.sleep(1)  # 시스템 리소스 초기화를 위한 시간
            main()
    else:
        main()

