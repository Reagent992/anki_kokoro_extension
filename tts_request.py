from dataclasses import dataclass

from aqt.editor import Editor

from .settings import Config


@dataclass(frozen=True)
class TTSRequest:
    """Dataclass for encapsulating TTS request data."""

    editor: Editor
    init_note_id: int | None
    field_index: int
    clean_text: str
    note_guid: str
    config: Config

