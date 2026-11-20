import importlib.util
from datetime import date
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / ".claude/skills/concept-author/sources.py"
spec = importlib.util.spec_from_file_location("sources", SCRIPT)
assert spec and spec.loader
sources = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sources)

URL = "https://docs.python.org/3/library/sys.html#sys.getrecursionlimit"


def keep(source: Path, day: int, body: str) -> Path:
    page = f"<p>{body}</p><p>Last updated on Nov {day}, 2026 (0{day % 10}:27 UTC).</p>"
    return sources.fetch(URL, source, date(2026, 11, day), page.encode(), "text/html")


def test_a_fetch_is_kept_in_a_folder_named_by_its_date(tmp_path):
    """The snapshot of one fetch is `library/<source>/<fetched_on>/`."""
    kept = keep(sources.folder(URL, tmp_path), 15, "A.")
    assert kept == tmp_path / "library" / "docs.python.org-3-library-sys.html" / "2026-11-15"
    assert sorted(p.name for p in kept.iterdir()) == ["meta.json", "page-001.txt", "source.html"]


def test_a_fetch_differing_by_its_build_stamp_alone_adds_nothing(tmp_path):
    """A docs.python.org rebuild moves the "Last updated on" line alone."""
    source = sources.folder(URL, tmp_path)
    first = keep(source, 15, "A.")
    assert keep(source, 20, "A.") == first
    assert sources.snapshots(source) == [first]


def test_a_fetch_whose_text_moved_is_kept_beside_the_last(tmp_path):
    """An edited page is a new snapshot, and the old one stays by its date."""
    source = sources.folder(URL, tmp_path)
    first = keep(source, 15, "A.")
    moved = keep(source, 20, "B.")
    assert sources.snapshots(source) == [first, moved]
    assert "A." in (first / "page-001.txt").read_text()
