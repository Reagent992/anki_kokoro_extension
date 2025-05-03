from dataclasses import dataclass
from pathlib import Path

# Constants
CREATE_SPEECH_ENDPOINT = "/v1/audio/speech"
HEALCH_CHECK_URL = "/health"
DEFAULT_AUDIO_FORMAT = "mp3"
DEFAULT_VOICE = "af_heart"
FILE_NAME_LEN = 10
## health check
RETRY_DELAY = 0.2
RETIRES_NUMBER = 10


@dataclass(frozen=True)
class Config:
    voice: str = "af_heart"
    api_url: str = "http://127.0.0.1:8880"
    autostart: bool = False
    path_to_exec: Path = Path()
    audio_format: str = DEFAULT_AUDIO_FORMAT
