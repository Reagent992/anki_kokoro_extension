from unittest.mock import patch

import pytest

from ..utils import create_config, sanitize_filename, strip_html


@pytest.mark.parametrize(
    "text,expected",
    [
        ("hello world", "hello_world"),
        ("file:name/with*bad|chars?", "filenamewithbadchars"),
        ("   spaced   text   ", "spaced_text"),
        ("", "file"),
        ("a" * 20, "a" * 10),
    ],
)
def test_sanitize_filename(text, expected):
    assert sanitize_filename(text) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        ("<p>Hello <b>world</b></p>", "Hello world"),
        ("<div>Test</div>", "Test"),
        ("Plain text", "Plain text"),
        (
            "<p>\u041f\u0440\u0438\u0432\u0435\u0442</p>",
            "\u041f\u0440\u0438\u0432\u0435\u0442",
        ),
        ("<div></div>", ""),
        (
            "<div>Text with <i>italic</i> and <u>underline</u></div>",
            "Text with italic and underline",
        ),
        ("<span>Clean</span>", "Clean"),
        (
            "<p>Multiple<br>lines</p>",
            "Multiplelines",
        ),
        ("<div><p><b>Nested</b> tags</p></div>", "Nested tags"),
        ("<ul><li>One</li><li>Two</li><li>Three</li></ul>", "OneTwoThree"),
        ("", ""),
        ("<div></div>", ""),
        ("<p><br></p>", ""),
        ("Plain text", "Plain text"),
        ("<p>&amp; &lt; &gt;</p>", "& < >"),
        ("<div>Broken", "Broken"),
        ("<p>Unclosed <b>bold", "Unclosed bold"),
        ("<div>Multiple <i>levels</div>", "Multiple levels"),
        ("<script>alert('hi');</script>Text", "alert('hi');Text"),
        ("<style>body{color:red;}</style>Visible", "body{color:red;}Visible"),
        ("<p>Привет, <b>мир</b>!</p>", "Привет, мир!"),
        ("<p>你好，<b>世界</b>！</p>", "你好，世界！"),
    ],
)
def test_strip_html(html, expected):
    assert strip_html(html) == expected


def test_create_config():
    mock_config = {
        "voice": "af_heart",
        "api_url": "http://127.0.0.1:8880",
        "autostart": "true",
        "path_to_kokoro_executable": "/tmp/kokoro.sh",
        "audio_format": "mp3",
        "shutdown_by_timer": "false",
    }
    with patch("anki_extension.utils.mw") as mw_mock:
        mw_mock.addonManager.getConfig.return_value = mock_config
        config = create_config()
        assert config.voice == "af_heart"
        assert config.api_url == "http://127.0.0.1:8880"
        assert config.autostart is True
        assert str(config.path_to_exec) == "/tmp/kokoro.sh"
        assert config.audio_format == "mp3"
        assert config.shutdown_by_timer is False
