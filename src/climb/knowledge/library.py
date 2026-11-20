"""The library of a module's sources: docs/authoring/concepts.md gives the
layout."""

import re
from datetime import date
from pathlib import Path

UNCOMMITTED = ("wikipedia.org",)
# docs.python.org rebuilds daily, and a rebuild moves this line alone
STAMPS = (re.compile(r"^\s*Last updated on .+ \(\d\d:\d\d UTC\)\.\s*$", re.M),)
ANCHOR = re.compile(r"\[#[^\]\n]*\]")
ELIDED = "[...]"
PAGE = re.compile(r"^page=(\d+)$")


def name(url: str) -> str:
    bare = url.split("#")[0].split("://", 1)[-1]
    return re.sub(r"[^A-Za-z0-9.]+", "-", bare).strip("-")[:120]


def committed(url: str) -> bool:
    return not url.split("#")[0].split("://", 1)[-1].split("/")[0].endswith(UNCOMMITTED)


def snapshots(source: Path) -> list[Path]:
    if not source.is_dir():
        return []
    return sorted(p for p in source.iterdir() if (p / "meta.json").exists())


def read_in(source: Path, on: date | None) -> Path | None:
    """The snapshot a reader on `on` read: the latest fetched by then, or the
    latest of all where no date is given."""
    kept = [p for p in snapshots(source) if on is None or p.name <= on.isoformat()]
    return kept[-1] if kept else None


def text(snapshot: Path) -> list[str]:
    pages = [p.read_text() for p in sorted(snapshot.glob("page-*.txt"))]
    for stamp in STAMPS:
        pages = [stamp.sub("", page) for page in pages]
    return pages


def holds_anchor(snapshot: Path, fragment: str) -> bool:
    if page := PAGE.match(fragment):
        return (snapshot / f"page-{int(page[1]):03}.txt").exists()
    return any(f"[#{fragment}]" in page for page in text(snapshot))


def holds_quote(snapshot: Path, quote: str) -> bool:
    """Whitespace aside, with the anchor marks the text carries dropped, and
    each part between `[...]` found after the last."""
    parts = [squeeze(part) for part in quote.split(ELIDED)]
    return any(_in_order(parts, squeeze(ANCHOR.sub("", page))) for page in text(snapshot))


def _in_order(parts: list[str], page: str) -> bool:
    at = 0
    for part in parts:
        found = page.find(part, at)
        if found < 0:
            return False
        at = found + len(part)
    return True


def squeeze(text: str) -> str:
    return " ".join(text.split())
