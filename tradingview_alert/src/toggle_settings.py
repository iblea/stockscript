"""
토글 설정 관리 모듈
프로그램 재시작 후에도 설정이 유지되도록 파일로 저장
"""

import json
import os
from threading import Lock
from typing import Optional


class ToggleSettings:
    """토글 설정을 관리하는 클래스"""

    def __init__(self, settings_file: str = "toggle_settings.json"):
        # 프로젝트 루트 디렉토리 기준으로 conf 디렉토리에 설정 파일 저장
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # src의 상위 디렉토리 (프로젝트 루트)
        conf_dir = os.path.join(project_root, "conf")

        # conf 디렉토리가 없으면 생성
        if not os.path.exists(conf_dir):
            os.makedirs(conf_dir)

        self.settings_file = os.path.join(conf_dir, settings_file)
        self.lock = Lock()
        self.settings = {
            "mantra_alert_enabled": True,  # 기본값: 활성화
        }
        self._load_settings()

    def _load_settings(self) -> None:
        """파일에서 설정 로드 (내부 메서드)"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
                print(f"토글 설정 로드: {self.settings}")
            except Exception as e:
                print(f"토글 설정 로드 실패: {e}")
        else:
            print("토글 설정 파일이 없습니다. 기본값 사용.")
            self._save_settings()

    def load_settings(self) -> None:
        """파일에서 설정 로드 (외부 호출용)"""
        with self.lock:
            self._load_settings()

    def _save_settings(self) -> None:
        """설정을 파일로 저장 (내부 메서드)"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            print(f"토글 설정 저장: {self.settings}")
        except Exception as e:
            print(f"토글 설정 저장 실패: {e}")

    def save_settings(self) -> None:
        """설정을 파일로 저장 (외부 호출용)"""
        with self.lock:
            self._save_settings()

    def is_mantra_alert_enabled(self) -> bool:
        """mantra/adi 알림이 활성화되어 있는지 확인"""
        with self.lock:
            return self.settings.get("mantra_alert_enabled", True)

    def set_mantra_alert(self, enabled: bool) -> None:
        """mantra/adi 알림 활성화/비활성화 설정"""
        with self.lock:
            self.settings["mantra_alert_enabled"] = enabled
            self._save_settings()

    def toggle_mantra_alert(self) -> bool:
        """mantra/adi 알림 토글 (활성화 ↔ 비활성화)"""
        current = self.is_mantra_alert_enabled()
        self.set_mantra_alert(not current)
        return not current


# 전역 인스턴스
toggle_settings = ToggleSettings()
