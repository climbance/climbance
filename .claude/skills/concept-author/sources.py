"""Read a module's source from the library: `sources.py <url> [--on <date>]`
prints the folder of the snapshot that date names, or of the latest, and the
date it was fetched. `docs/authoring/concepts.md` gives the layout.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

from climb.knowledge.library import committed, download, fetch, name, snapshots

ENGINE = Path(__file__).resolve().parents[3]
CACHE = ENGINE / "data" / "sources"


def folder(url: str, content: Path) -> Path:
    return (content / "library" if committed(url) else CACHE) / name(url)


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
