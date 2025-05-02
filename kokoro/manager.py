import requests
import os
import signal
from subprocess import Popen
from time import sleep
from ..settings import HEALCH_CHECK_URL, RETIRES_NUMBER, RETRY_DELAY, Config


class KokoroManager:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._process: Popen | None = None
        self._is_kokoro_up: bool = False

    def shutdown_kokoro(self) -> None:
        if self._process is not None:
            os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)

    def is_running(self) -> bool:
        return self._is_kokoro_up

    def health_status(self) -> bool:
        try:
            requests.get(
                self.config.api_url + HEALCH_CHECK_URL,
            ).raise_for_status()
        except requests.ConnectionError:
            return False
        return True

    def wait_for_api_ready(
        self,
        retries: int = RETIRES_NUMBER,
        delay: float = RETRY_DELAY,
    ) -> bool:
        for attemp in range(retries):
            if self.health_status():
                self._is_kokoro_up = True
                return True
            sleep(delay * attemp)
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
