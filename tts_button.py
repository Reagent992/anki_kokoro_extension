from __future__ import annotations

from typing import ClassVar

from aqt import mw
from aqt.editor import Editor
from aqt.operations import QueryOp
from aqt.utils import showInfo

from .manager import KokoroManager
from .settings import Config
from .utils import create_config, sanitize_filename, strip_html


class TTSButton:
    """
    The object of this class is created by opening the ANKI card editor.

    -  `__call__` method is called when the TTS button(UI) is pressed.
    -  `__init__` called every time card editor is open.
    """

    config: ClassVar[Config] = create_config()
    kokoro: ClassVar[KokoroManager] = KokoroManager(config)

    def __init__(self) -> None:
        self._field_index: int
        self._editor: Editor
        self._user_input: str | None

    def __call__(self, editor: Editor) -> None:
        """This function will be called by pressing a button"""
        self._editor = editor
        self._user_input = self._read_user_input()
        if not self._user_input:
            showInfo("Please select a field and highlight text.")
            return
        self.dispatcher()

    def dispatcher(self) -> None:
        if TTSButton.kokoro.is_running():
            self.run_tts()
        elif not TTSButton.kokoro.is_running() and TTSButton.config.autostart:
            self.startup_kokoro_process()
        else:
            showInfo("Kokoro is down and autostart is turned off")

    def run_tts(self) -> None:
        if self._user_input:
            self.clean_text = strip_html(self._user_input)
            QueryOp(
                parent=mw,
                op=lambda _: TTSButton.kokoro.send_request(self.clean_text),  # type: ignore
                success=self._send_request_callback,
            ).without_collection().run_in_background()

    def startup_kokoro_process(self) -> None:
        QueryOp(
            parent=mw,
            op=lambda _: TTSButton.kokoro.start_kokoro(),  # type: ignore
            success=self._start_kokoro_callback,
        ).without_collection().run_in_background()
        if self.config.shutdown_by_timer:
            self.kokoro.start_idle_timer()

    def _read_user_input(self) -> str | None:
        assert self._editor.web and self._editor.note
        if self._editor.web.editor.currentField in (None, ""):
            return None
        self._field_index = self._editor.web.editor.currentField
        if page := self._editor.web.page():
            return page.selectedText()

    def _add_media_to_collection(self, content: bytes) -> str:
        assert mw.col
        file_name = f"{sanitize_filename(self.clean_text)}.{self.config.audio_format}"
        return mw.col.media.write_data(
            file_name,
            content,
        )

    def _fill_field_with_audio(self, content: bytes) -> None:
        assert self._editor.web and self._editor.note
        filename = self._add_media_to_collection(content)
        current_text = self._editor.note.fields[self._field_index]
        self._editor.note.fields[self._field_index] = (
            current_text + f"[sound:{filename}]"
        )
        self._editor.loadNote()

    def _send_request_callback(self, content: bytes) -> None:
        self._fill_field_with_audio(content)

    def _start_kokoro_callback(self, result: bool) -> None:
        if result:
            self.run_tts()

    @classmethod
    def shutdown_kokoro(cls) -> None:
        if hasattr(cls, "kokoro") and cls.kokoro:
            cls.kokoro.shutdown_kokoro()
