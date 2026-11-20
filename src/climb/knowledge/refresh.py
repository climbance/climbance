"""The library refresh: docs/authoring/concepts.md gives what it moves."""

import json
import re
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from difflib import SequenceMatcher, get_close_matches
from pathlib import Path
from typing import Any

from climb.knowledge.concepts import read_concepts, sources
from climb.knowledge.library import (
    ANCHOR,
    ELIDED,
    PAGE,
    committed,
    download,
    fetch,
    holds_anchor,
    holds_quote,
    name,
    snapshots,
    squeeze,
    text,
)

SENTENCE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Broken:
    module: str
    file: str
    concept: str
    url: str
    # the quote, or `#<fragment>` for an anchor
    held: str
    # the passage of the new snapshot most like the quote, or the anchors most
    # like the fragment
    now: str
    snapshot: str


@dataclass
class Refreshed:
    unchanged: list[str] = field(default_factory=list[str])
    changed: list[str] = field(default_factory=list[str])
    failed: dict[str, str] = field(default_factory=dict[str, str])
    moved: list[str] = field(default_factory=list[str])
    broken: list[Broken] = field(default_factory=list[Broken])


def refresh(
    modules: list[Path],
    library: Path,
    on: date,
    get: Callable[[str], tuple[bytes, str]] = download,
) -> Refreshed:
    found = Refreshed()
    cited = {root: read_concepts(root, []) for root in modules}
    urls = sorted(
        {
            url.split("#")[0]
            for concepts in cited.values()
            for concept in concepts.values()
            for url in sources(concept)
            if committed(url)
        }
    )
    for url in urls:
        source = library / name(url)
        last = (snapshots(source) or [None])[-1]
        try:
            kept = fetch(url, source, on, *get(url))
        except Exception as error:  # one page down leaves the rest to refresh
            found.failed[url] = f"{type(error).__name__}: {error}"
            continue
        if kept == last:
            meta = json.loads((kept / "meta.json").read_text())
            (kept / "meta.json").write_text(
                json.dumps(meta | {"checked_on": on.isoformat()}, indent=2) + "\n"
            )
            found.unchanged.append(url)
        else:
            found.changed.append(url)
    changed = set(found.changed)
    for root, concepts in cited.items():
        for key, concept in concepts.items():
            urls = [u for u in sources(concept) if committed(u)]
            if not changed & {u.split("#")[0] for u in urls}:
                continue
            broken = _broken(root, key, concept, urls, library)
            found.broken += broken
            if not broken and isinstance(concept.get("read_on"), date):
                _move(root / concept["_file"], key, on)
                found.moved.append(f"{root.name} {key}")
    return found


def _broken(
    root: Path, key: str, concept: dict[str, Any], urls: list[str], library: Path
) -> list[Broken]:
    """What the latest snapshots of a concept's sources no longer hold."""
    found: list[Broken] = []
    latest: dict[str, Path] = {}
    for url in urls:
        kept = snapshots(library / name(url))
        if not kept:
            continue
        latest[url] = kept[-1]
        fragment = url.partition("#")[2]
        if fragment and not holds_anchor(kept[-1], fragment):
            near = _anchors_like(kept[-1], fragment)
            found.append(
                Broken(root.name, concept["_file"], key, url, f"#{fragment}", near, kept[-1].name)
            )
    quote = concept.get("quote")
    if (
        isinstance(quote, str)
        and latest
        and not any(holds_quote(s, quote) for s in latest.values())
    ):
        url, snapshot, now = max(
            ((u, s, _passage(s, quote)) for u, s in latest.items()), key=lambda f: f[2][0]
        )
        found.append(Broken(root.name, concept["_file"], key, url, quote, now[1], snapshot.name))
    return found


def _anchors_like(snapshot: Path, fragment: str) -> str:
    if PAGE.match(fragment):
        return f"{len(list(snapshot.glob('page-*.txt')))} pages"
    ids = [m[0][2:-1] for page in text(snapshot) for m in ANCHOR.finditer(page)]
    near = get_close_matches(fragment, ids, n=3, cutoff=0.5)
    return ", ".join(f"#{n}" for n in near) or "no anchor alike"


def _passage(snapshot: Path, quote: str) -> tuple[float, str]:
    """The run of sentences most like the quote, as many as the quote holds."""
    wanted = squeeze(" ".join(quote.split(ELIDED)))
    width = len(SENTENCE.split(wanted))
    best = (0.0, "")
    for page in text(snapshot):
        sentences = SENTENCE.split(squeeze(ANCHOR.sub("", page)))
        for at in range(max(1, len(sentences) - width + 1)):
            window = " ".join(sentences[at : at + width])
            matcher = SequenceMatcher(None, wanted, window, autojunk=False)
            if (
                matcher.real_quick_ratio() > best[0]
                and matcher.quick_ratio() > best[0]
                and (ratio := matcher.ratio()) > best[0]
            ):
                best = (ratio, window)
    return best


def _move(path: Path, key: str, on: date) -> None:
    """Rewrite one concept's `read_on` line, keeping the file's layout."""
    lines = path.read_text().splitlines(keepends=True)
    start = next(i for i, line in enumerate(lines) if line.strip() == f'id = "{key}"')
    for i in range(start, len(lines)):
        if lines[i].startswith("[["):
            break
        if lines[i].startswith("read_on = "):
            lines[i] = f"read_on = {on.isoformat()}\n"
            break
    path.write_text("".join(lines))
    concepts = tomllib.loads(path.read_text())["concept"]
    if next(c for c in concepts if c["id"] == key).get("read_on") != on:
        raise ValueError(f"{path}: the read_on of {key} did not move")
