from __future__ import annotations

import logging
from typing import ClassVar

from aqt import mw
from aqt.editor import Editor
from aqt.operations import QueryOp
from aqt.utils import showInfo

from .manager import KokoroManager
from .settings import Config
from .tts_output_processor import TTSOutputProcessor
from .tts_request import TTSRequest
from .utils import create_config, strip_html

logger = logging.getLogger(__name__)


class TTSButton:
    """
    The object of this class is created by opening the ANKI card editor.

    One editor can create multiple notes.
    `__call__` method is called when the TTS button(UI) is pressed.
    """

    config: ClassVar[Config] = create_config()
    kokoro: ClassVar[KokoroManager] = KokoroManager(config)

    def __call__(self, editor: Editor) -> None:
        """This method will be called by pressing a button."""
        self._editor = editor
        self._init_note_id = editor.note.id if editor.note and editor.note.id else None
        self._init_note_guid = editor.note.guid if editor.note else ""
        logger.info("New Note GUID: %s", self._init_note_guid)
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

            # Save request info in advance,
            # There is a chance that it will be overwritten by a new note
            request = TTSRequest(
                editor=self._editor,
                init_note_id=self._init_note_id,
                field_index=self._field_index,
                clean_text=self.clean_text,
                init_note_guid=self._init_note_guid,
                config=TTSButton.config,
            )

            def _send_request_callback(content: bytes) -> None:
                """
                Callback triggered when TTS content is ready.
                Delegate the processing and insertion of audio to TTSOutputProcessor.
                """
                processor = TTSOutputProcessor(request)
                processor.process_audio(content)

            QueryOp(
                parent=mw,
                op=lambda _: TTSButton.kokoro.send_request(self.clean_text),  # type: ignore
                success=_send_request_callback,
            ).without_collection().run_in_background()

    def startup_kokoro_process(self) -> None:
        QueryOp(
            parent=mw,
            op=lambda _: TTSButton.kokoro.start_kokoro(),  # type: ignore
            success=self._start_kokoro_callback,
        ).without_collection().run_in_background()
        if TTSButton.config.shutdown_by_timer:
            TTSButton.kokoro.start_idle_timer()

    def _read_user_input(self) -> str | None:
        assert self._editor.web and self._editor.note
        if self._editor.web.editor.currentField in (None, ""):
            return None
        self._field_index = self._editor.web.editor.currentField
        if page := self._editor.web.page():
            return page.selectedText()

    def _start_kokoro_callback(self, result: bool) -> None:
        if result:
            self.run_tts()

    @classmethod
    def shutdown_kokoro(cls) -> None:
        cls.kokoro.shutdown_kokoro()
