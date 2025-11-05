from __future__ import annotations

import logging
from typing import ClassVar, cast

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
    An instance of this class is created when opening the Anki card editor.

    One editor can create multiple notes, i.e. the value of the `editor.note`
    variable can be changed at any time.

    `__call__` method is called when the TTS button(UI) is pressed.
    """

    config: ClassVar[Config] = create_config()
    kokoro: ClassVar[KokoroManager] = KokoroManager(config)

    def __call__(self, editor: Editor) -> None:
        """This method will be called by pressing a button."""
        self._editor = editor
        self._field_index = 0
        self._user_input = self._read_user_input()
        if not self._user_input:
            showInfo("Please select a field and highlight text.")
            return
        self.request = self._create_request()
        self.dispatcher()

    def dispatcher(self) -> None:
        if TTSButton.kokoro.is_running:
            self.run_tts(self.request)
        elif not TTSButton.kokoro.is_running and TTSButton.config.autostart:
            self.startup_kokoro_process(self.request)
        else:
            showInfo("Kokoro is not running and autostart is disabled")

    def run_tts(self, request: TTSRequest) -> None:
        def _send_request_callback(content: bytes) -> None:
            """
            Callback triggered when TTS content is ready.
            Delegate the processing and insertion of audio to TTSOutputProcessor.
            """
            processor = TTSOutputProcessor(request)
            processor.process_audio(content)

        logger.info("Sending tts query for: %s", request.clean_text)
        QueryOp(
            parent=mw,
            op=lambda _: TTSButton.kokoro.send_request(request.clean_text),
            success=_send_request_callback,
        ).without_collection().run_in_background()

    def startup_kokoro_process(self, request: TTSRequest) -> None:
        def _start_kokoro_callback(result: bool) -> None:
            if result:
                self.run_tts(request)
            else:
                logger.warning("Failed to get response from KokoroTTS server")

        QueryOp(
            parent=mw,
            op=lambda _: TTSButton.kokoro.start_kokoro(),
            success=_start_kokoro_callback,
        ).without_collection().run_in_background()
        if TTSButton.config.shutdown_by_timer:
            TTSButton.kokoro.start_idle_timer()

    def _create_request(self) -> TTSRequest:
        init_note_id = (
            self._editor.note.id if self._editor.note and self._editor.note.id else None
        )
        init_note_guid = self._editor.note.guid if self._editor.note else ""
        logger.info("Note GUID: %s", init_note_guid)
        return TTSRequest(
            editor=self._editor,
            init_note_id=init_note_id,
            field_index=self._field_index,
            clean_text=strip_html(cast(str, self._user_input)),
            init_note_guid=init_note_guid,
            config=TTSButton.config,
        )

    def _read_user_input(self) -> str | None:
        assert self._editor.web
        if self._editor.web.editor.currentField in (None, ""):
            return None
        self._field_index = self._editor.web.editor.currentField
        if page := self._editor.web.page():
            return page.selectedText()

    @classmethod
    def shutdown_kokoro(cls) -> None:
        cls.kokoro.shutdown_kokoro()
