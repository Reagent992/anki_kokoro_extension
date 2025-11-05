from dataclasses import dataclass

from aqt.editor import Editor

from .settings import Config


@dataclass(frozen=True)
class TTSRequest:
    """Data class that encapsulates TTS request data."""

    editor: Editor
    init_note_id: int | None
    field_index: int
    clean_text: str
    init_note_guid: str
    config: Config
