import requests


from ..settings import (
    CREATE_SPEECH_ENDPOINT,
    Config,
)


def _send_request(string: str, config: Config) -> requests.Response:
    return requests.post(
        config.api_url + CREATE_SPEECH_ENDPOINT,
        json={
            "input": string,
            "voice": config.voice,
        },
    )


def send_request(string: str, config: Config) -> bytes:
    return _send_request(string, config).content
