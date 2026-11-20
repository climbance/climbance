"""The library of a module's sources: docs/authoring/concepts.md gives the
layout."""

import json
import re
import shutil
import subprocess
import tempfile
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

UNCOMMITTED = ("wikipedia.org",)
# docs.python.org rebuilds daily, and a rebuild moves this line alone
STAMPS = (re.compile(r"^\s*Last updated on .+ \(\d\d:\d\d UTC\)\.\s*$", re.M),)
ANCHOR = re.compile(r"\[#[^\]\n]*\]")
ELIDED = "[...]"
PAGE = re.compile(r"^page=(\d+)$")
SKIPPED = {"script", "style", "nav", "header", "footer"}


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


class Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skipping = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SKIPPED:
            self.skipping += 1
        anchor = dict(attrs).get("id")
        if anchor and not self.skipping:
            self.parts.append(f"\n[#{anchor}]\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIPPED and self.skipping:
            self.skipping -= 1
        if tag in {"p", "div", "li", "h1", "h2", "h3", "h4", "pre", "tr", "br"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skipping:
            self.parts.append(data)


def download(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "source-cache"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read(), response.headers.get_content_type()


def write(url: str, body: bytes, kind: str, into: Path, on: date) -> None:
    into.mkdir(parents=True)
    if kind == "application/pdf" or body[:5] == b"%PDF-":
        (into / "source.pdf").write_bytes(body)
        extracted = subprocess.run(
            ["pdftotext", "-layout", str(into / "source.pdf"), "-"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        pages = extracted.split("\f")
        if pages and not pages[-1].strip():
            pages.pop()
    else:
        (into / "source.html").write_bytes(body)
        parser = Text()
        parser.feed(body.decode("utf-8", errors="replace"))
        pages = [re.sub(r"\n\s*\n+", "\n\n", "".join(parser.parts))]
    for number, page in enumerate(pages, 1):
        (into / f"page-{number:03}.txt").write_text(page)
    meta = {"url": url, "fetched_on": on.isoformat(), "pages": len(pages)}
    (into / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")


def fetch(url: str, source: Path, on: date, body: bytes, kind: str) -> Path:
    """Keep the fetch as the snapshot of `on`, unless its text matches."""
    with tempfile.TemporaryDirectory() as scratch:
        fresh = Path(scratch) / "snapshot"
        write(url.split("#")[0], body, kind, fresh, on)
        if (kept := snapshots(source)) and text(kept[-1]) == text(fresh):
            return kept[-1]
        into = source / on.isoformat()
        shutil.rmtree(into, ignore_errors=True)
        source.mkdir(parents=True, exist_ok=True)
        shutil.move(fresh, into)
        return into
