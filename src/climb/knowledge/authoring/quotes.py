"""Rule 30: docs/authoring/rules.md."""

from datetime import date
from pathlib import Path

from climb.knowledge.authoring.course import Course, Report
from climb.knowledge.concepts import sources
from climb.knowledge.library import committed, holds_anchor, holds_quote, name, read_in


def quoted(course: Course, report: Report) -> None:
    """Each source is in the library and holds its anchor, and a quote is in
    the snapshot its `read_on` names."""
    library = course.root.parent.parent / "library"
    for key, concept in course.concepts.items():
        at = f"{concept['_file']} {key}"
        quote = concept.get("quote")
        on = concept.get("read_on") if isinstance(concept.get("read_on"), date) else None
        read: list[Path] = []
        for url in sources(concept):
            if not committed(url):
                if quote is not None:
                    report.error(30, at, f"quotes beside {url}, which git does not hold")
                continue
            snapshot = read_in(library / name(url), on)
            if snapshot is None:
                report.error(30, at, f"no snapshot of {url}{f' by {on}' if on else ''}")
                continue
            read.append(snapshot)
            fragment = url.partition("#")[2]
            if fragment and not holds_anchor(snapshot, fragment):
                report.error(30, at, f"snapshot {snapshot.name} of {url} holds no #{fragment}")
        if isinstance(quote, str) and read and not any(holds_quote(s, quote) for s in read):
            report.error(30, at, f"no snapshot it cites holds the quote {quote[:50]!r}")
