# dev description

## TODO

- If you close editor window durring TTS work this error occured:

```python
Anki 25.07.5 (7172b2d2) (ao)
Python 3.13.5 Qt 6.9.1 PyQt 6.9.1
Platform: Linux-6.15.9-arch1-1-x86_64-with-glibc2.42

Traceback (most recent call last):
  File "/usr/lib/python3.13/site-packages/aqt/taskman.py", line 152, in raise_exception
    raise exception
  File "/usr/lib/python3.13/site-packages/aqt/taskman.py", line 148, in _on_closures_pending
    closure()
    ~~~~~~~^^
  File "/usr/lib/python3.13/site-packages/aqt/taskman.py", line 88, in <lambda>
    lambda future: self.run_on_main(lambda: on_done(future))
                                            ~~~~~~~^^^^^^^^
  File "/usr/lib/python3.13/site-packages/aqt/operations/__init__.py", line 261, in wrapped_done
    self._success(future.result())
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/home/rea/.local/share/Anki2/addons21/anki_kokoro_extension/tts_button.py", line 92, in _send_request_callback
    self._fill_field_with_audio(content)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
  File "/home/rea/.local/share/Anki2/addons21/anki_kokoro_extension/tts_button.py", line 83, in _fill_field_with_audio
    assert self._editor.web and self._editor.note
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError

===Add-ons (active)===
(add-on provided name [Add-on folder, installed at, version, is config changed])
'' ['anki_kokoro_extension', 0, 'None', '']
AutoDefine - Automatically define vocabulary words pronunciations images ['2136497008', 2023-11-09T06:03, 'None', mod]
ReColor ['688199788', 2025-01-28T14:23, '3.1', mod]

===IDs of active AnkiWeb add-ons===
2136497008 688199788

===Add-ons (inactive)===
(add-on provided name [Add-on folder, installed at, version, is config changed])
```
To fix this issue, we should probably edit the card through the Anki database rather than editing it directly.

