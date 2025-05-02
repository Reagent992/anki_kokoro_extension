# Что это?
It's a **ANKI** extension that integrates [KokoroTTS-FastAPI]() into anki in a blunt way.

## Requirements
- ANKI
- UNIX OS(Creating and manipulating a session of processes only works on unix.)

## About autostart KokoroTTS
- It's optional feature.
- It's unstable. For example KokoroTTS-FastAPI will keep works in background if anki crash.
- It's works only on unix os due to how child processes controlled.
- Shutdown triggered by `profile_will_close` hook(Called before one-way syncs and colpkg imports/exports.).


