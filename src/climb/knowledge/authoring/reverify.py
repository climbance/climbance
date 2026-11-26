"""`climb module reverify`: each due claim's `model_witness` run on the panel,
and its checks appended to the concept file. docs/authoring/concepts.md"""

import io
import json
import re
import tomllib
from collections.abc import Callable, Iterator
from contextlib import redirect_stdout
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from climb.knowledge.authoring.course import Course
from climb.knowledge.authoring.model_checks import due, malformed

type Ask = Callable[[str, str], str]

VERDICTS = {"holds": True, "fails": False}
HEADER = re.compile(r"\s*\[")
QUOTES = re.compile(r"'''|\"\"\"")


@dataclass(frozen=True)
class Check:
    concept: str
    model: str
    checked_on: date
    holds: bool
    measured: str


def owed(course: Course, today: date) -> dict[str, list[str]]:
    """Each claim depending on a model, and the panel models it is due on."""
    panel = course.models.get("panel", [])
    every = course.models.get("every_days", 0)
    found = {
        name: due(concept.get("checks", []), panel, every, today)
        for name, concept in course.concepts.items()
        if "model_witness" in concept and not malformed(concept.get("checks", []))
    }
    return {name: models for name, models in found.items() if models}


def witnessed(code: str, model: str, ask: Ask) -> tuple[bool, str]:
    """The verdict on the witness's last line, and the line above it."""
    out = io.StringIO()
    # in-process: `ask` sends through the engine's calls, which a subprocess
    # could not reach. A witness is authored content, run as the check runs it
    with redirect_stdout(out):
        exec(code, {"__name__": "__main__", "ask": ask, "model": model})
    lines = [line.strip() for line in out.getvalue().splitlines() if line.strip()]
    if len(lines) < 2 or lines[-1] not in VERDICTS:
        raise ValueError("the witness's last two lines are not the measured sizes and a verdict")
    return VERDICTS[lines[-1]], lines[-2]


def appended(path: Path, checks: list[Check]) -> None:
    """Append the checks to their concepts as `[[concept.checks]]` tables."""
    text = path.read_text()
    for name in dict.fromkeys(c.concept for c in checks):
        text = _inserted(text, name, [c for c in checks if c.concept == name])
    before = {c["id"]: c.get("checks", []) for c in tomllib.loads(path.read_text())["concept"]}
    try:
        after = {c["id"]: c.get("checks", []) for c in tomllib.loads(text)["concept"]}
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"{path}: write checks as [[concept.checks]] tables ({error})") from error
    for name in before:
        wanted = before[name] + [_fields(c) for c in checks if c.concept == name]
        if after[name] != wanted:
            raise ValueError(f"{path}: the checks of {name} did not land as written")
    path.write_text(text)


def _fields(check: Check) -> dict[str, Any]:
    return {
        "model": check.model,
        "checked_on": check.checked_on,
        "holds": check.holds,
        "measured": check.measured,
    }


def _inserted(text: str, name: str, checks: list[Check]) -> str:
    lines = text.splitlines(keepends=True)
    headers = list(_headers(lines))
    bounds = [*headers, len(lines)]
    wanted = f"id = {json.dumps(name)}"
    start = next(
        (
            i
            for i, after in zip(headers, bounds[1:], strict=True)
            if lines[i].strip() == "[[concept]]"
            and any(line.strip() == wanted for line in lines[i:after])
        ),
        None,
    )
    if start is None:
        raise ValueError(f"no [[concept]] with id {name}")
    later = [i for i in headers if i > start and not lines[i].strip().startswith("[[concept.")]
    end = later[0] if later else len(lines)
    # trailing blanks and comments belong to whatever follows the concept
    while end > start + 1 and (not lines[end - 1].strip() or lines[end - 1].startswith("#")):
        end -= 1
    if lines[end - 1] and not lines[end - 1].endswith("\n"):
        lines[end - 1] += "\n"
    tables = "".join(
        f"\n[[concept.checks]]\nmodel = {json.dumps(c.model)}\nchecked_on = {c.checked_on}\n"
        f"holds = {str(c.holds).lower()}\nmeasured = {json.dumps(c.measured)}\n"
        for c in checks
    )
    return "".join(lines[:end]) + tables + "".join(lines[end:])


def _headers(lines: list[str]) -> Iterator[int]:
    """The index of each table header, skipping multi-line strings, where a
    witness's output may start with `[`."""
    inside: str | None = None
    for i, line in enumerate(lines):
        if inside is None and HEADER.match(line):
            yield i
        for quote in QUOTES.findall(line):
            if inside is None:
                inside = quote
            elif quote == inside:
                inside = None
