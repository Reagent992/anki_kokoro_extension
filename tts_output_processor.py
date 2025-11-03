from __future__ import annotations

import logging

from anki.notes import Note, NoteId
from aqt import mw
from aqt.operations import CollectionOp

from .tts_request import TTSRequest
from .utils import sanitize_filename

logger = logging.getLogger(__name__)


class TTSOutputProcessor:
    """
    Handles the insertion of TTS-generated audio into an Anki note.

    This class receives audio content produced by a TTS engine, adds it to the
    collection's media folder, and updates the target note's field with a playable
    audio tag. It manages different editor modes and handles cases where the
    editor may be closed.
    """

    def __init__(self, request: TTSRequest) -> None:
        self._editor = request.editor
        self._field_index = request.field_index
        self._init_note_id = request.init_note_id
        self._clean_text = request.clean_text
        self._init_note_guid = request.init_note_guid
        self.config = request.config
        logger.info(
            "Request data:\n%s",
            "\n".join(f"{k:<20} = {v}" for k, v in request.__dict__.items()),
        )

    @property
    def note(self) -> Note | None:
        note = None
        if self._editor.note and self._editor.note.guid == self._init_note_guid:
            note = self._editor.note
            logger.info("Note passed id: %s", note.id)
            return note
        if self._init_note_id:
            logger.info("Note loaded from _init_note_id")
            note = mw.col.get_note(NoteId(self._init_note_id)) if mw.col else None
        elif self._init_note_guid:
            logger.info("Note loaded from guid")
            note = self._get_note_by_guid()
        return note

    def process_audio(self, content: bytes) -> None:
        """
        Main entry point to process and insert TTS audio into the note.

        Args:
            content: The raw audio bytes produced by the TTS engine.
        """

        # Determine the note to update and check if audio addition is still needed
        note = self.note
        if not note:
            logger.warning("Audio not added: note not found")
            return
        filename = self._add_media_to_collection(content)
        # get tag and play audio
        tag = self._editor.fnameToLink(filename)
        if self._should_use_webview_update():
            # Update note through webview if card editor is open
            self._append_tag_through_webview(note, tag)
        else:
            # Update existing note in the collection
            self._update_note_in_collection(note, tag)

    def _should_use_webview_update(self) -> bool:
        if not self._editor.web or not self._editor.note:
            return False
        return self._editor.note.guid == self._init_note_guid

    def _add_media_to_collection(self, content: bytes) -> str:
        """Add the audio bytes to the Anki media collection and return the filename."""
        assert mw.col
        file_name = f"{sanitize_filename(self._clean_text)}.{self.config.audio_format}"
        return mw.col.media.write_data(
            file_name,
            content,
        )

    def _append_tag_through_webview(self, note: Note, tag: str) -> None:
        logger.info("Adding audio tag through webview")
        js = f"""
        (function() {{
            try {{
                const fields = document.querySelectorAll('.rich-text-editable');
                const field = fields[{self._field_index}]?.shadowRoot?.querySelector('anki-editable');
                if (!field) {{
                    return {{ result: false, error: 'field {self._field_index} not found' }};
                }}
                field.textContent += "{tag}";
                field.dispatchEvent(new InputEvent("input", {{ bubbles: true }}));
                return {{ result: true }};
            }} catch (e) {{
                return {{ result: false, error: e.message || String(e) }};
            }}
        }})();
        """

        assert self._editor.web
        self._editor.web.evalWithCallback(
            js, lambda result: self._handle_webview_result(result, note, tag)
        )

    def _handle_webview_result(self, result: dict, note: Note, tag: str) -> None:
        logger.info("Webview append result: %s", result)
        if not result or not result.get("result"):
            logger.warning(
                "Append tag through webview failed, fallback to default version"
            )
            self._update_note_in_collection(note, tag)

    def _get_note_by_guid(self) -> Note | None:
        """
        Check if the note associated with the stored GUID exists in the collection.

        This method queries the database for a note by its GUID (stored during TTS initiation)
        to handle cases where the editor is closed but audio needs to be added to a saved note.
        Returns the Note object if found and valid, otherwise None.
        """
        try:
            note_id_result = mw.col.db.execute(  # pyright: ignore[reportOptionalMemberAccess]
                "SELECT id FROM notes WHERE guid = ?", self._init_note_guid
            )
            if not note_id_result:
                return None
            note_id = note_id_result[0][0]
            note = mw.col.get_note(note_id)  # pyright: ignore[reportOptionalMemberAccess]
            logger.info(f"Found note by GUID: {note}")
            return note
        except Exception as e:
            logger.error(f"Error retrieving note by GUID {self._init_note_guid}: {e}")
            return None

    def _update_note_in_collection(self, note: Note, tag: str) -> None:
        """Update the given note in the collection asynchronously."""
        logger.info("Adding an audio tag through collection")
        current_text = note.fields[self._field_index]
        note.fields[self._field_index] = current_text + tag
        CollectionOp(
            parent=mw,
            op=lambda col: col.update_note(note, skip_undo_entry=True),
            # skip_undo_entry=True due to: Ctrl+Z cancels the audio tag entry.
        ).run_in_background()
