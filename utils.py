import re
import unicodedata
from html.parser import HTMLParser

from .settings import FILE_NAME_LEN


def sanitize_filename(text: str, max_length: int = FILE_NAME_LEN) -> str:
    text = "".join(c for c in text if c.isprintable())
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "", text)
    text = re.sub(r"\s+", "_", text).strip("_")
    if len(text) > max_length:
        text = text[:max_length]
    if not text:
        text = "file"
    return text


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.fed = []

    def handle_data(self, data: str) -> None:
        self.fed.append(data)

    def get_data(self) -> str:
        return "".join(self.fed)


def strip_html(html: str) -> str:
    stripper = HTMLStripper()
    stripper.feed(html)
    return stripper.get_data()
