import os
import signal
import time
from subprocess import Popen
from time import sleep

import requests
from aqt.qt import QTimer

from .settings import (
    CHECK_INTERVAL_MSEC,
    HEALTH_CHECK_URL,
    IDLE_TIMEOUT_SEC,
    RETRIES_NUMBER,
    RETRY_DELAY,
    TTS_ENDPOINT,
    Config,
)


class KokoroManager:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._process: Popen | None = None
        self._is_kokoro_up: bool = False
        self._last_used: float = time.time()
        self._idle_timer: QTimer | None = None

    def _on_idle_check(self) -> None:
        if time.time() - self._last_used > IDLE_TIMEOUT_SEC:
            self.shutdown_kokoro()
            self._idle_timer = None

    def start_idle_timer(self) -> None:
        """Must be started from the main thread."""
        if self._idle_timer is None:
            self._idle_timer = QTimer()
            self._idle_timer.setInterval(CHECK_INTERVAL_MSEC)
            self._idle_timer.timeout.connect(self._on_idle_check)
        self._idle_timer.start()

    def shutdown_kokoro(self) -> None:
        if self._process is not None:
            os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
            self._is_kokoro_up = False
            self._process = None

    def is_running(self) -> bool:
        return self._is_kokoro_up

    def health_status(self) -> bool:
        try:
            requests.get(
                self.config.api_url + HEALTH_CHECK_URL,
            ).raise_for_status()
        except requests.ConnectionError:
            return False
        return True

    def wait_for_api_ready(
        self,
        retries: int = RETRIES_NUMBER,
        delay: float = RETRY_DELAY,
    ) -> bool:
        for attempt in range(retries):
            if self.health_status():
                self._is_kokoro_up = True
                return True
            sleep(delay * attempt)
        raise TimeoutError()

    def _create_process(self) -> Popen:
        return Popen(
            self.config.path_to_exec,
            cwd=self.config.path_to_exec.parent,
            start_new_session=True,
        )

    def start_kokoro(self) -> bool:
        self._process = self._create_process()
        return self.wait_for_api_ready()

    def send_request(self, string: str) -> bytes:
        self._last_used = time.time()
        return requests.post(
            self.config.api_url + TTS_ENDPOINT,
            json={
                "input": string,
                "voice": self.config.voice,
            },
        ).content
