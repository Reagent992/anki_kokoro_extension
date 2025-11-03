import logging

from aqt.editor import Editor
from aqt.gui_hooks import editor_did_init_buttons, profile_will_close

from .tts_button import TTSButton

logger = logging.getLogger(__name__)


def add_button(buttons: list[str], editor: Editor) -> None:
    """Add button to editor menu."""
    new_button = editor.addButton(
        None,
        "TTS",
        TTSButton(),
        tip="Create TTS (Ctrl+Shift+T)",
        keys="Ctrl+Shift+T",
    )
    buttons.append(new_button)


logger.info("KokoroTTS extension is loaded")
editor_did_init_buttons.append(add_button)
profile_will_close.append(TTSButton.shutdown_kokoro)
