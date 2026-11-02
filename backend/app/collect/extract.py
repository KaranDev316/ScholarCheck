"""Readable page text from an official-source HTML page.

The snapshot body is what every excerpt is matched against, so extraction is
narrow by design: drop scripts, styles and page chrome, keep block structure as
line breaks, and never let inline markup split a sentence. CMS templates also
leave escaped markup behind (``</p>\\n<h3>`` inside a JSON field), so a second
pass strips tags that survived unescaping.

Preferring a page's ``main`` region keeps navigation and search chrome out of
the retained text; when a page has no usable main region the whole body is kept,
because a noisy snapshot still quotes real text while a truncated one invents
silence.
"""

import html
import re
from html.parser import HTMLParser

# Subtrees whose text is never page content.
SUBTREES_DROPPED = frozenset(
    {
        "audio",
        "button",
        "canvas",
        "embed",
        "form",
        "head",
        "iframe",
        "math",
        "noscript",
        "object",
        "option",
        "script",
        "select",
        "style",
        "svg",
        "template",
        "textarea",
        "video",
    }
)

# Site furniture that surrounds the content.
CHROME = frozenset({"aside", "footer", "header", "nav"})

BLOCK = frozenset(
    {
        "address",
        "article",
        "blockquote",
        "br",
        "caption",
        "dd",
        "div",
        "dl",
        "dt",
        "figcaption",
        "figure",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "hr",
        "li",
        "main",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "tbody",
        "td",
        "tfoot",
        "th",
        "thead",
        "tr",
        "ul",
    }
)

MAIN = frozenset({"article", "main"})

EMBEDDED_TAG = re.compile(r"</?[a-zA-Z][^<>]{0,200}>")
SPACE = re.compile(r"[^\S\n]+")
BLANK_LINES = re.compile(r"\n{2,}")
ESCAPED_NEWLINE = re.compile(r"\\[rn]")


class _Renderer(HTMLParser):
    """Collect text, breaking on block elements and skipping chrome."""

    def __init__(self, *, only_main: bool) -> None:
        super().__init__(convert_charrefs=True)
        self.only_main = only_main
        self.chunks: list[str] = []
        self._dropped: list[str] = []
        self._main: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SUBTREES_DROPPED:
            self._dropped.append(tag)
            return
        if tag in CHROME:
            self._dropped.append(tag)
            return
        if tag in MAIN or dict(attrs).get("role") == "main":
            self._main.append(tag)
        self._emit_break(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._emit_break(tag)

    def handle_endtag(self, tag: str) -> None:
        if self._dropped and self._dropped[-1] == tag:
            self._dropped.pop()
            return
        if self._main and self._main[-1] == tag:
            self._main.pop()
        self._emit_break(tag)

    def handle_data(self, data: str) -> None:
        if self._dropped:
            return
        if self.only_main and not self._main:
            return
        self.chunks.append(data)

    def _emit_break(self, tag: str) -> None:
        if self._dropped or tag not in BLOCK:
            return
        if self.only_main and not self._main:
            return
        self.chunks.append("\n")


def extract_text(markup: str) -> str:
    """Return the readable text of ``markup``, or ``""`` when there is none."""

    preferred = _render(markup, only_main=True)
    if len(preferred) >= 400:
        return preferred
    return _render(markup, only_main=False)


def _render(markup: str, *, only_main: bool) -> str:
    renderer = _Renderer(only_main=only_main)
    renderer.feed(markup)
    renderer.close()

    text = "".join(renderer.chunks)
    for _ in range(2):
        text = ESCAPED_NEWLINE.sub("\n", text)
        text = EMBEDDED_TAG.sub("\n", text)
        text = html.unescape(text)

    text = text.replace("\u00a0", " ").replace("\u2009", " ").replace("\r", "\n")
    lines = (SPACE.sub(" ", line).strip() for line in text.split("\n"))
    return BLANK_LINES.sub("\n", "\n".join(line for line in lines if line)).strip()


__all__ = ["extract_text"]
