import logging
import os
import signal
import subprocess
import time

import requests
from aqt.qt import QTimer

from .settings import (
    CHECK_INTERVAL_MSEC,
    HEALTH_CHECK_TIMEOUT,
    HEALTH_CHECK_URL,
    RETRIES_NUMBER,
    RETRY_DELAY,
    TTS_ENDPOINT,
    TTS_REQUEST_TIMEOUT,
    Config,
)

logger = logging.getLogger(__name__)


class KokoroManager:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._process: subprocess.Popen | None = None
        self._last_used: float = time.time()
        self._idle_timer: QTimer | None = None

    def _on_idle_check(self) -> None:
        if time.time() - self._last_used > self.config.idle_timeout_in_seconds:
            self.shutdown_kokoro()
            self._idle_timer = None

    def start_idle_timer(self) -> None:
        """Must be called from the main thread."""
        if self._idle_timer is None:
            self._idle_timer = QTimer()
            self._idle_timer.setInterval(CHECK_INTERVAL_MSEC)
            self._idle_timer.timeout.connect(self._on_idle_check)
        self._idle_timer.start()

    def shutdown_kokoro(self) -> None:
        logger.info("Shutting down Kokoro")
        if self._process is not None:
            os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
            self._process = None
        else:
            logger.warning("There is nothing to Shutdown")

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def health_status(self) -> bool:
        try:
            requests.get(
                self.config.api_url + HEALTH_CHECK_URL,
                timeout=HEALTH_CHECK_TIMEOUT,
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
                return True
            time.sleep(delay * attempt)
        raise TimeoutError(
            "Kokoro TTS server failed to start within the expected time. "
            "Please check if the server is properly configured and accessible."
        )

    def _create_process(self) -> subprocess.Popen:
        logger.info("Launching kokoro")
        return subprocess.Popen(
            self.config.path_to_exec,
            cwd=self.config.path_to_exec.parent,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def start_kokoro(self) -> bool:
        self._process = self._create_process()
        return self.wait_for_api_ready()

    def send_request(self, input_text: str) -> bytes:
        self._last_used = time.time()
        if not self.health_status():
            self.wait_for_api_ready()
        return requests.post(
            self.config.api_url + TTS_ENDPOINT,
            json={
                "input": input_text,
                "voice": self.config.voice,
            },
            timeout=TTS_REQUEST_TIMEOUT,
        ).content
