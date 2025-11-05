# Development Documentation

## TODO

- [x] Update existing notes in the collection in the background. This allows us to close the editor before TTS finishes its work.
- [x] Fixed `TimeoutError`: the default startup time has increased from 1 to 10 seconds.
- [x] Add keyboard shortcut (Ctrl+SHIFT+T)
- [x] Anything inserted while TTS is loading is overwritten (deleted).
- [x] FIXME: There is a chance that Kokoro will be started twice.

## features backlog

- Should we use the TTS for the whole line if nothing is selected? Or just alert is fine?

## dev tips

- Launch anki through terminal to access the logs
- To open devtools use `QTWEBENGINE_REMOTE_DEBUGGING=8080 anki` then go to `http://localhost:8080/` in Chromium
- Press `Ctrl+shift+;` in the main window to access REPL.
- launch anki with the test profile using `anki -p <profile_name>`

## Implementation details

- The Editor object represents an open editor window. One editor can create multiple notes.

### Adding audio tag to a card

Problems:

- `self._editor.note` is created by pressing the TTS button, the text entered during loading is available only through webview.
- `self._editor.note` exists while the UI window is open. The TTS load is slow, so we need to add an audio tag even after the UI window has been closed.
- Default methods for inserting text into a card are not suitable.

To solve these problems, some fragile logic was added (like SQL queries and JavaScript in the webview).
