import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# 로그 디렉토리 생성

LOG_SCRIPT_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR= LOG_SCRIPT_DIR + "/logs/"


# 로거 설정
def setup_logger(name, log_file, level=logging.INFO):
    """로거를 설정하는 함수"""
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # )
    formatter = logging.Formatter(
        '%(asctime)s|%(filename)s:%(lineno)d|%(levelname)s| %(message)s',
        # '%(asctime)s|%(filename)s:%(lineno)d %(funcName)s|%(levelname)s| %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # handler = logging.FileHandler(log_file, encoding='utf-8')
    handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',  # 자정마다 로테이션
        interval=1,       # 1일 간격
        backupCount=7,   # 최대 7개 파일 보관
        encoding='utf-8'
    )
    handler.suffix = "%Y%m%d"
    handler.setFormatter(formatter)

    # logger = logging.getLogger(name)
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(handler)

    # 콘솔 출력도 추가
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def default_logfile():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    """기본 로그 파일 경로를 반환하는 함수"""
    # return f'{LOG_DIR}/kiwoom_{datetime.now().strftime("%Y%m%d")}.log'
    return f'{LOG_DIR}/kiwoom.log'

# 로거 생성
logger = None



# 사용 예제
def login_example():
    global logger

    logger = setup_logger(
        'kiwoom_login',
        default_logfile()
    )

    logger.info("로그인 프로세스 시작")

    try:
        # 로그인 로직
        logger.debug("디버그 정보: 연결 시도 중...")
        logger.info("키움 API 연결 성공")

    except Exception as e:
        logger.error(f"로그인 실패: {str(e)}")
        logger.exception("상세 에러 정보")

    finally:
        logger.info("로그인 프로세스 완료")

if __name__ == "__main__":
    login_example()