from collections import deque
from threading import Lock, Thread, Condition
from typing import Optional, Deque
from time import sleep
import threading


class RWLock:
    # 읽기-쓰기 락 구현 클래스
    def __init__(self):
        self._read_ready = Condition(Lock())  # 조건 변수
        self._readers = 0  # 현재 읽기 중인 스레드 수
        self._writers = 0  # 현재 쓰기 중인 스레드 수
        self._write_waiting = 0  # 쓰기 대기 중인 스레드 수

    def acquire_read(self):
        # 읽기 락 획득
        with self._read_ready:
            # 쓰기 작업이 진행 중이거나 대기 중인 경우 대기
            while self._writers > 0 or self._write_waiting > 0:
                self._read_ready.wait()
            self._readers += 1

    def release_read(self):
        # 읽기 락 해제
        with self._read_ready:
            self._readers -= 1
            # 마지막 읽기가 종료되면 쓰기 스레드에게 신호
            if self._readers == 0:
                self._read_ready.notify_all()

    def acquire_write(self):
        # 쓰기 락 획득
        with self._read_ready:
            self._write_waiting += 1
            # 읽기나 쓰기 작업이 진행 중인 경우 대기
            while self._readers > 0 or self._writers > 0:
                self._read_ready.wait()
            self._write_waiting -= 1
            self._writers += 1

    def release_write(self):
        # 쓰기 락 해제
        with self._read_ready:
            self._writers -= 1
            # 모든 대기 중인 스레드에게 신호
            self._read_ready.notify_all()


class SafeDeque:
    # RWLock을 사용한 thread-safe deque 구현
    def __init__(self, maxlen: int = None):
        self._deque: Deque[str] = deque(maxlen=maxlen)
        self._rwlock = RWLock()
        self._event = threading.Event()  # 새로운 데이터 알림용

    def push(self, value: str) -> bool:
        stat = True
        # deque에 값을 추가 (쓰기 작업)
        self._rwlock.acquire_write()
        try:
            self._deque.append(value)
            self._event.set()  # 새로운 데이터가 있음을 알림
        except Exception as e:
            print(e)
            stat = False
        finally:
            self._rwlock.release_write()
        return stat

    def pop(self) -> Optional[str]:
        # deque에서 값을 제거하고 반환 (쓰기 작업)
        self._rwlock.acquire_write()
        try:
            if not self._deque:
                self._event.clear()  # 데이터가 없음을 표시
                return None
            return self._deque.popleft()
        finally:
            self._rwlock.release_write()

    def is_empty(self) -> bool:
        # deque가 비었는지 확인 (읽기 작업)
        self._rwlock.acquire_read()
        try:
            return len(self._deque) == 0
        finally:
            self._rwlock.release_read()

    def get_item(self, index: int) -> Optional[str]:
        # deque의 특정 인덱스 항목 조회 (읽기 작업)
        self._rwlock.acquire_read()
        try:
            if index >= len(self._deque):
                return None
            return self._deque[index]
        except IndexError:
            return None
        finally:
            self._rwlock.release_read()

    def size(self) -> int:
        # deque의 크기 반환 (읽기 작업)
        self._rwlock.acquire_read()
        try:
            return len(self._deque)
        finally:
            self._rwlock.release_read()

    def wait_for_data(self, timeout: float = 0.1) -> bool:
        # 데이터가 들어올 때까지 대기
        return self._event.wait(timeout)



class SafeString:
    # RWLock을 사용한 thread-safe 문자열 관리 클래스
    def __init__(self, initial_value: str = ""):
        self._value = initial_value
        self._rwlock = RWLock()

    def get_value(self) -> str:
        # 문자열 읽기 (읽기 작업)
        self._rwlock.acquire_read()
        try:
            return self._value
        finally:
            self._rwlock.release_read()

    def set_value(self, new_value: str) -> None:
        # 문자열 수정 (쓰기 작업)
        self._rwlock.acquire_write()
        try:
            self._value = new_value
        finally:
            self._rwlock.release_write()

    def append(self, text: str) -> None:
        # 문자열 추가 (쓰기 작업)
        self._rwlock.acquire_write()
        try:
            self._value += text
        finally:
            self._rwlock.release_write()



# 전역변수
msg_queue = SafeDeque(maxlen=100)

safe_string = SafeString()

mantra_string = SafeString()

adi_string = SafeString()





"""
# 사용 예제

def producer():
    global msg_queue
    # 생산자 스레드 - 1초마다 데이터 생성
    counter = 1
    while True:
        message = f"Hello World{counter}"
        msg_queue.push(message)
        print(f"Produced: {message}")
        counter += 1
        sleep(1)  # 1초 대기


def consumer():
    global msg_queue
    # 소비자 스레드 - 0.1초마다 큐 체크 및 데이터 처리
    while True:
        # 데이터가 들어올 때까지 최대 0.1초 대기
        if msg_queue.wait_for_data(0.1):
            if not msg_queue.is_empty():
                # # 읽기 작업: 큐의 상태 확인
                # size = msg_queue.size()
                # if size > 0:
                #     first_item = msg_queue.get_item(0)
                #     print(f"Queue size: {size}, First item: {first_item}")
                # 쓰기 작업: 모든 항목 처리
                data = ""
                while True:
                    tmp = msg_queue.pop()
                    if not tmp:
                        break
                    data += tmp
                if data != "":
                    print(f"Consumed: {data}")
        else:
            print("Queue is empty, waiting...")

        sleep(0.1)  # 0.1초마다 체크


def main():
    # 전역 queue 사용
    global msg_queue

    # 생산자와 소비자 스레드 생성
    producer_thread = Thread(target=producer, daemon=True)
    consumer_thread = Thread(target=consumer, daemon=True)

    # 스레드 시작
    producer_thread.start()
    consumer_thread.start()

    try:
        # 메인 스레드가 종료되지 않도록 대기
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다...")


if __name__ == "__main__":
    main()

"""