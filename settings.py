from dataclasses import dataclass
from pathlib import Path
from typing import Final

# Constants
TTS_ENDPOINT: Final = "/v1/audio/speech"
HEALTH_CHECK_URL: Final = "/health"
DEFAULT_AUDIO_FORMAT: Final = "mp3"
DEFAULT_VOICE: Final = "af_heart"
FILE_NAME_LEN: Final = 10
HEALTH_CHECK_TIMEOUT: Final = 5
TTS_REQUEST_TIMEOUT: Final = 40
## health check
RETRY_DELAY: Final = 1
RETRIES_NUMBER: Final = 10
## shutdown by timeout
CHECK_INTERVAL_MSEC: Final = 10_000  # 60_000 = 1 minute


@dataclass(frozen=True)
class Config:
    voice: str = "af_heart"
    api_url: str = "http://127.0.0.1:8880"
    autostart: bool = False
    path_to_exec: Path = Path()
    audio_format: str = DEFAULT_AUDIO_FORMAT
    shutdown_by_timer: bool = False
    idle_timeout_in_seconds: int = 60 * 2
