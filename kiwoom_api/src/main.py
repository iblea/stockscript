from time import sleep
import logutil

def main():
    logutil.logger = logutil.setup_logger(
        'kiwoom_login',
        logutil.default_logfile()
    )


    while True:
        logutil.logger.info("Hello World")
        sleep(10)


if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        logutil.logger.info("\nProgram interrupted by user")

    finally:
        # 정리 작업
        # cleanup_pid_file()
        logutil.logger.info("Cleanup completed")
