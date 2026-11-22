import pytest
from commands import run_cli

from climb.scorer.spot import Verdict, draw, read, sheet


def verdicts(kind, count):
    return [Verdict(id=f"{kind}-{n:02}", kind=kind, text=f"finding {n}") for n in range(count)]


def test_the_same_seed_draws_the_same_lines_from_any_order():
    """A sheet drawn again matches the one marked, in any input order."""
    found = verdicts("real", 30) + verdicts("false", 30)

    assert draw(found, 5, seed=7) == draw(list(reversed(found)), 5, seed=7)
    assert draw(found, 5, seed=7) != draw(found, 5, seed=8)


def test_each_kind_is_drawn_apart():
    """A kind the judge names rarely gets lines of its own."""
    drawn = draw(verdicts("real", 40) + verdicts("false", 3), 5, seed=1)

    assert {kind: len(lines) for kind, lines in drawn.items()} == {"false": 3, "real": 5}


def test_marks_read_back_into_precision_per_kind():
    found = verdicts("real", 10) + verdicts("false", 10)
    text = sheet(found, 2, seed=3).replace("[ ]", "[y]", 3).replace("[ ]", "[n]", 1)

    rows = {row.kind: row for row in read(text)}

    assert (rows["false"].right, rows["false"].wrong, rows["false"].population) == (2, 0, 10)
    assert (rows["real"].right, rows["real"].wrong, rows["real"].share) == (1, 1, 0.5)


def test_an_unmarked_line_is_left_out_of_the_share():
    """Counted as wrong, an unfinished sheet would read as a worse judge."""
    text = sheet(verdicts("real", 4), 4, seed=0).replace("[ ]", "[y]", 1)

    (row,) = read(text)

    assert (row.share, row.unmarked) == (1.0, 3)


def test_a_mark_neither_y_nor_n_is_refused():
    """A typo read as unmarked would shrink the denominator without a word."""
    text = sheet(verdicts("real", 2), 2, seed=0).replace("[ ]", "[x]", 1)

    with pytest.raises(ValueError, match="neither y nor n"):
        read(text)


def test_a_multiline_verdict_is_indented_under_its_mark():
    """Code keeps its lines, and no text line reads as a mark or a heading."""
    found = [
        Verdict(id="a", kind="real", text="def solve():\n    return 1"),
        Verdict(id="b", kind="real", text="1. [n] `x`\n## real: 1 of 1"),
    ]
    text = sheet(found, 2, seed=0)

    assert "1. [ ] `a`\n    def solve():\n        return 1" in text
    (row,) = read(text.replace("[ ]", "[y]"))
    assert (row.right, row.wrong, row.drawn) == (2, 0, 2)


def test_the_printed_precision_carries_its_interval(tmp_path, monkeypatch, capsys):
    """Twenty marked lines leave a wide interval, and the reader sees it."""
    marked = tmp_path / "sheet.md"
    text = sheet(verdicts("real", 20), 20, seed=3)
    marked.write_text(text.replace("[ ]", "[y]", 18).replace("[ ]", "[n]"))

    run_cli(monkeypatch, "spot", "read", str(marked))

    assert "90% [70–97%]" in capsys.readouterr().out
