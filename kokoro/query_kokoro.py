import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
import requests

from ..settings import (
    CREATE_SPEECH_ENDPOINT,
    DEFAULT_AUDIO_FORMAT,
    DEFAULT_VOICE,
    FILE_NAME_LEN,
    LOCAL_API_URL,
)


@dataclass(frozen=True)
class UserInput:
    input: str
    voice: str = DEFAULT_VOICE


def _send_request(user_input: UserInput) -> requests.Response:
    return requests.post(
        LOCAL_API_URL + CREATE_SPEECH_ENDPOINT, json=asdict(user_input)
    )


def save_response_as_audio_file(response: requests.Response) -> Path:
    file_name = f"{uuid.uuid4().hex[:FILE_NAME_LEN]}.{DEFAULT_AUDIO_FORMAT}"
    file = Path.cwd() / file_name
    file.write_bytes(response.content)
    return file


def send_request(string: str, voice: str = DEFAULT_VOICE) -> Path:
    user_input: UserInput = UserInput(string, voice)
    request = _send_request(user_input)
    return save_response_as_audio_file(request)
