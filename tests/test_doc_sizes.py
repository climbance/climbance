import re
from pathlib import Path

ARCHITECTURE = Path(__file__).resolve().parent.parent / "docs" / "architecture"
# `concepts/repo-constraints.md` gives both limits and the reason for them.
MOST_LINES = 200
MOST_BULLETS = 12


def unfenced(path: Path) -> list[str]:
    lines, fenced = [], False
    for line in path.read_text().splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced:
            lines.append(line)
    return lines


def bullets_per_heading(lines: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    heading = "(before any heading)"
    for line in lines:
        if line.startswith("#"):
            heading = line
        elif re.match(r"[-*] ", line):
            counts[heading] = counts.get(heading, 0) + 1
    return counts


def test_no_architecture_doc_runs_past_the_line_limit():
    """A fenced block is not counted, so the generated views and a wireframe
    fit. A component over the limit becomes a folder."""
    over = [
        f"{path.relative_to(ARCHITECTURE)}: {len(lines)}"
        for path in sorted(ARCHITECTURE.rglob("*.md"))
        if len(lines := unfenced(path)) > MOST_LINES
    ]
    assert over == []


def test_no_heading_in_the_architecture_holds_too_many_bullets():
    """Top-level bullets alone count: a nested list belongs to its bullet."""
    over = [
        f"{path.relative_to(ARCHITECTURE)}: {heading} ({count})"
        for path in sorted(ARCHITECTURE.rglob("*.md"))
        for heading, count in bullets_per_heading(unfenced(path)).items()
        if count > MOST_BULLETS
    ]
    assert over == []


def test_the_bullet_count_skips_nested_and_fenced_lists(tmp_path: Path):
    """A nested bullet and a `-` inside a fence are not top-level bullets."""
    doc = tmp_path / "doc.md"
    doc.write_text("# A\n- one\n  - nested\n```\n- fenced\n```\n## B\n- two\n* three\n")
    assert bullets_per_heading(unfenced(doc)) == {"# A": 1, "## B": 2}
