from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from aqt import mw
from aqt.editor import Editor
from aqt.operations import QueryOp
from aqt.utils import showInfo

from .kokoro.query_kokoro import send_request
from .kokoro.start_kokoro import start_kokoro
from .parser import strip_html

"""
- [x] Добавить кнопку
- [x] Считать выделенный текст или использовать весь введеный текст.
- [x] Заставить кнопку выполнять request в api.
  - [x] Делать это без блокировки UI.
- [x] Добавлять полученный результат в медиатеку ANKI
- [x] Чистить полученный текст от html
- [x] При повторном нажание читается весь инпут, а не только выделенный текст
- [x] remove prints
- [ ] Перенести настройки в json
- [ ] Сделать функцию для чтения настроек внутри класса.
- [ ] Сделать автозапуск kokoro_tts
    По нажатию кнопки перевода, kokoro_tts будет запускаться, и работать до момента закрытия ANKI.
    Надо ли запускаться будет проверка по health эндпоинту.
"""


@dataclass(frozen=True)
class Config:
    voice: str = "af_heart"
    api_url: str = "http://127.0.0.1:8880"


def create_config() -> Config:
    config = mw.addonManager.getConfig(__name__)
    assert config, "Something wrong with plugin config"
    return Config(
        voice=config["voice"],
        api_url=config["api_url"],
    )


class TTSButton:
    _instance: ClassVar[TTSButton | None] = None
    _is_kokoro_up: ClassVar[bool] = False
    _config: ClassVar[Config | None] = None

    def __init__(self) -> None:
        TTSButton._instance = self
        if not TTSButton._is_kokoro_up:
            start_kokoro()
            TTSButton._is_kokoro_up = True
        if not TTSButton._config:
            TTSButton._config = create_config()

    def read_user_input(self, editor: Editor) -> str | None:
        assert editor.web and editor.note
        if editor.web.editor.currentField in ("", None):
            return
        self.field_index = editor.web.editor.currentField
        page = editor.web.page()
        if page:
            selected_text = page.selectedText()
            return selected_text

    def add_media_to_collection(self, file: Path) -> str:
        assert mw.col
        new_file_name = mw.col.media.add_file(str(file))
        file.unlink(missing_ok=True)
        return new_file_name

    def fill_field_with_audio(self, file: Path):
        assert self.editor.web
        assert self.editor.note
        filename = self.add_media_to_collection(file)
        current_text = self.editor.note.fields[self.field_index]
        self.editor.note.fields[self.field_index] = current_text + f"[sound:{filename}]"
        self.editor.loadNote()

    def __call__(self, editor: Editor) -> None:
        """This function will be called by pressing a button"""
        self.editor = editor
        if not (user_input := self.read_user_input(self.editor)):
            showInfo("Please select a field and highlight text.")
            return
        clean_text = strip_html(user_input)
        if TTSButton._config is not None:
            QueryOp(
                parent=mw,
                op=lambda _: send_request(clean_text, voice=TTSButton._config.voice),
                success=TTSButton.callback,
            ).without_collection().run_in_background()

    @classmethod
    def callback(cls, file: Path) -> None:
        assert cls._instance
        cls._instance.fill_field_with_audio(file)
