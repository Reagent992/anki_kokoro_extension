from aqt.editor import Editor
from aqt.gui_hooks import editor_did_init_buttons, profile_will_close
from .tts_button import TTSButton


def add_button(buttons: list[str], editor: Editor):
    """Add button to editor menu."""
    new_button = editor.addButton(
        None,
        "TTS",
        TTSButton(),
    )
    buttons.append(new_button)


editor_did_init_buttons.append(add_button)
profile_will_close.append(TTSButton.shutdown_kokoro)
