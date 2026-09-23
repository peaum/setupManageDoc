"""Extract audio-chunk markers from rendered HTML or source QMD."""
from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup

_QMD_DIV = re.compile(
    r"::: \{\.audio-chunk(?:\s+#(?P<id>[^\s}]+))?[^}]*\}\s*(?P<body>.*?)\s*:::",
    re.DOTALL,
)


def _clean(text: str) -> str:
    return " ".join(text.split())


def extract_from_html(path: Path) -> list[tuple[str, str]]:
    """Extract chunks from HTML, using a wrapping section ID when needed."""
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    chunks: list[tuple[str, str]] = []
    for index, element in enumerate(soup.select("div.audio-chunk"), start=1):
        identifier = element.get("id")
        if not identifier:
            parent = element.find_parent(["section", "article"])
            identifier = parent.get("id") if parent else None
        identifier = identifier or f"chunk-{index}"
        text = _clean(element.get_text(" ", strip=True))
        if text:
            chunks.append((identifier, text))
    return chunks


def extract_from_qmd(path: Path) -> list[tuple[str, str]]:
    """Extract Pandoc fenced audio divs from a QMD source file."""
    chunks: list[tuple[str, str]] = []
    for index, match in enumerate(_QMD_DIV.finditer(path.read_text(encoding="utf-8")), start=1):
        identifier = match.group("id") or f"chunk-{index}"
        text = _clean(BeautifulSoup(match.group("body"), "html.parser").get_text(" ", strip=True))
        if text:
            chunks.append((identifier, text))
    return chunks
