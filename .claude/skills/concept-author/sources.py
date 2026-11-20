"""Read a module's source from the library: `sources.py <url> [--on <date>]`
prints the folder of the snapshot that date names, or of the latest, and the
date it was fetched. `docs/authoring/concepts.md` gives the layout.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[3]
CACHE = ENGINE / "data" / "sources"
UNCOMMITTED = ("wikipedia.org",)
SKIPPED = {"script", "style", "nav", "header", "footer"}
# docs.python.org rebuilds daily, and a rebuild moves this line alone
STAMPS = (re.compile(r"^\s*Last updated on .+ \(\d\d:\d\d UTC\)\.\s*$", re.M),)


class Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skipping = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
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


def folder(url: str, content: Path) -> Path:
    bare = url.split("#")[0]
    host = bare.split("://", 1)[-1].split("/")[0]
    name = re.sub(r"[^A-Za-z0-9.]+", "-", bare.split("://", 1)[-1]).strip("-")[:120]
    if host.endswith(UNCOMMITTED):
        return CACHE / name
    return content / "library" / name


def snapshots(source: Path) -> list[Path]:
    if not source.is_dir():
        return []
    return sorted(p for p in source.iterdir() if (p / "meta.json").exists())


def text(snapshot: Path) -> list[str]:
    pages = [p.read_text() for p in sorted(snapshot.glob("page-*.txt"))]
    for stamp in STAMPS:
        pages = [stamp.sub("", page) for page in pages]
    return pages


def download(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "source-cache"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read(), response.headers.get_content_type()


def write(url: str, body: bytes, kind: str, into: Path, on: date) -> dict:
    into.mkdir(parents=True)
    if kind == "application/pdf" or body[:5] == b"%PDF-":
        (into / "source.pdf").write_bytes(body)
        text = subprocess.run(
            ["pdftotext", "-layout", str(into / "source.pdf"), "-"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        pages = text.split("\f")
        if pages and not pages[-1].strip():
            pages.pop()
    else:
        (into / "source.html").write_bytes(body)
        parser = Text()
        parser.feed(body.decode("utf-8", errors="replace"))
        pages = [re.sub(r"\n\s*\n+", "\n\n", "".join(parser.parts))]
    for number, page in enumerate(pages, 1):
        (into / f"page-{number:03}.txt").write_text(page)
    meta = {
        "url": url,
        "fetched_on": on.isoformat(),
        "pages": len(pages),
    }
    (into / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    return meta


def fetch(url: str, source: Path, on: date, body: bytes, kind: str) -> Path:
    """Keep the fetch as the snapshot of `on`, unless its text matches."""
    bare = url.split("#")[0]
    with tempfile.TemporaryDirectory() as scratch:
        fresh = Path(scratch) / "snapshot"
        write(bare, body, kind, fresh, on)
        if (kept := snapshots(source)) and text(kept[-1]) == text(fresh):
            return kept[-1]
        into = source / on.isoformat()
        shutil.rmtree(into, ignore_errors=True)
        source.mkdir(parents=True, exist_ok=True)
        shutil.move(fresh, into)
        return into


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--content", type=Path, default=ENGINE / "content", help="the repository")
    parser.add_argument("--on", type=date.fromisoformat, help="the snapshot fetched on this date")
    parser.add_argument(
        "--refresh", action="store_true", help="fetch again, kept if the text moved"
    )
    args = parser.parse_args()
    source = folder(args.url, args.content)
    kept = snapshots(source)
    if args.on:
        into = source / args.on.isoformat()
        if into not in kept:
            sys.exit(f"no snapshot of {args.url} on {args.on}: {[p.name for p in kept]}")
    elif kept and not args.refresh:
        into = kept[-1]
    else:
        into = fetch(args.url, source, date.today(), *download(args.url.split("#")[0]))
    meta = json.loads((into / "meta.json").read_text())
    sys.stdout.write(f"{into}\nfetched {meta['fetched_on']}, {meta['pages']} page(s)\n")
    if wanted := re.search(r"#page=(\d+)", args.url):
        sys.stdout.write(f"{into / f'page-{int(wanted.group(1)):03}.txt'}\n")


if __name__ == "__main__":
    main()
