"""Read a module's source from the library: `sources.py <url>` prints the folder
holding its text, one file per PDF page, and the date it was fetched.

The library is `library/` in the content repository, committed: the original
file beside its text, so a cited `#page=` names a page of a copy git holds.
Wikipedia changes with every edit, so it is cached in the engine's gitignored
`data/` instead.
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[3]
CACHE = ENGINE / "data" / "sources"
UNCOMMITTED = ("wikipedia.org",)
SKIPPED = {"script", "style", "nav", "header", "footer"}


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


def fetch(url: str, into: Path) -> dict:
    bare = url.split("#")[0]
    request = urllib.request.Request(bare, headers={"User-Agent": "source-cache"})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read()
        kind = response.headers.get_content_type()
    into.mkdir(parents=True, exist_ok=True)
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
        "url": bare,
        "fetched_on": date.today().isoformat(),
        "pages": len(pages),
    }
    (into / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    return meta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--content", type=Path, default=ENGINE / "content", help="the repository")
    parser.add_argument("--refresh", action="store_true", help="fetch again, a new edition")
    args = parser.parse_args()
    into = folder(args.url, args.content)
    meta_path = into / "meta.json"
    if meta_path.exists() and not args.refresh:
        meta = json.loads(meta_path.read_text())
    else:
        meta = fetch(args.url, into)
    sys.stdout.write(f"{into}\nfetched {meta['fetched_on']}, {meta['pages']} page(s)\n")
    if wanted := re.search(r"#page=(\d+)", args.url):
        sys.stdout.write(f"{into / f'page-{int(wanted.group(1)):03}.txt'}\n")


if __name__ == "__main__":
    main()
