import json
from datetime import date
from pathlib import Path

from climb.knowledge.library import fetch, name
from climb.knowledge.refresh import refresh

URL = "https://docs.python.org/3/reference/compound_stmts.html"
HELD = "<p id='the-while-statement'>The loop retests its condition.</p>"
OLD = "<p id='the-while-statement'>The loop retests its condition. Then it stops.</p>"
TODAY = date(2026, 11, 20)


def module(tmp_path: Path, source: str, quote: str) -> Path:
    root = tmp_path / "modules" / "m"
    (root / "concepts" / "t").mkdir(parents=True)
    (root / "concepts" / "t" / "sub.toml").write_text(
        f'[[concept]]\nid = "while-retests"\nsource = "{source}"\n'
        f'quote = "{quote}"\nread_on = 2026-11-10\n\n'
        '[[concept]]\nid = "other"\nsource = "https://example.org/a"\n'
    )
    for url, page in ((URL, HELD), ("https://example.org/a", "A.")):
        library = tmp_path / "library" / name(url)
        fetch(url, library, date(2026, 11, 10), page.encode(), "text/html")
    return root


def served(pages: dict[str, str]):
    return lambda url: (pages[url].encode(), "text/html")


def test_an_unchanged_source_records_the_check(tmp_path):
    """A refetch with the same text adds no snapshot and stamps `checked_on`."""
    root = module(tmp_path, f"{URL}#the-while-statement", "The loop retests its condition.")
    found = refresh(
        [root], tmp_path / "library", TODAY, served({URL: HELD, "https://example.org/a": "A."})
    )
    assert found.changed == [] and len(found.unchanged) == 2
    meta = tmp_path / "library" / "docs.python.org-3-reference-compound-stmts.html"
    assert [p.name for p in meta.iterdir()] == ["2026-11-10"]
    assert json.loads((meta / "2026-11-10" / "meta.json").read_text())["checked_on"] == "2026-11-20"


def test_a_quote_the_new_snapshot_holds_moves_its_read_on(tmp_path):
    """A changed page still holding the quote moves `read_on` to today."""
    root = module(tmp_path, f"{URL}#the-while-statement", "The loop retests its condition.")
    found = refresh(
        [root], tmp_path / "library", TODAY, served({URL: OLD, "https://example.org/a": "A."})
    )
    assert found.changed == [URL] and found.broken == []
    assert found.moved == ["m while-retests"]
    text = (root / "concepts" / "t" / "sub.toml").read_text()
    assert "read_on = 2026-11-20" in text and 'id = "other"' in text


def test_a_quote_the_new_snapshot_lacks_is_reported_with_the_new_text(tmp_path):
    """The report gives the old sentence and the passage now most like it."""
    root = module(tmp_path, URL, "The loop retests its condition.")
    page = "<p>The loop re-evaluates its condition. Unrelated.</p>"
    found = refresh(
        [root], tmp_path / "library", TODAY, served({URL: page, "https://example.org/a": "A."})
    )
    [broken] = found.broken
    assert (broken.concept, broken.held) == ("while-retests", "The loop retests its condition.")
    assert broken.now == "The loop re-evaluates its condition."
    assert found.moved == []
    assert "read_on = 2026-11-10" in (root / "concepts" / "t" / "sub.toml").read_text()


def test_an_anchor_the_new_snapshot_lacks_is_reported(tmp_path):
    """A renamed anchor is reported with the anchors most like it."""
    root = module(tmp_path, f"{URL}#the-while-statement", "The loop retests its condition.")
    page = "<p id='while-statement'>The loop retests its condition.</p>"
    found = refresh(
        [root], tmp_path / "library", TODAY, served({URL: page, "https://example.org/a": "A."})
    )
    [broken] = found.broken
    assert (broken.held, broken.now) == ("#the-while-statement", "#while-statement")


def test_a_source_that_cannot_be_fetched_is_reported_and_the_rest_refresh(tmp_path):
    """One page down leaves the other sources refreshed."""
    root = module(tmp_path, URL, "The loop retests its condition.")

    def get(url: str) -> tuple[bytes, str]:
        if url == URL:
            raise OSError("down")
        return b"A.", "text/html"

    found = refresh([root], tmp_path / "library", TODAY, get)
    assert list(found.failed) == [URL] and found.unchanged == ["https://example.org/a"]
