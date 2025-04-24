import pytest
from ..parser import strip_html  # замени your_module на имя твоего файла


@pytest.mark.parametrize(
    "html, expected",
    [
        ("<p>Hello, <b>world</b>!</p>", "Hello, world!"),
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
