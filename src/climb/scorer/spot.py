"""A seeded spot check of a judge's verdicts: `cli/eval-set.md`."""

import json
import random
import re
from collections.abc import Iterable, Sequence

from pydantic import BaseModel

SAMPLE = 20  # per kind, as the reviewers' spot check drew
SEED = 20261120  # fixed, so a sheet drawn again matches the one marked
MARKS = {"y": True, "n": False}
_HEADING = re.compile(r"^## (?P<kind>.+): (?P<drawn>\d+) of (?P<population>\d+)$")
_LINE = re.compile(r"^\d+\. \[(?P<mark>.)\] `(?P<id>[^`]+)`")


class Verdict(BaseModel):
    id: str
    kind: str
    text: str


class Precision(BaseModel):
    kind: str
    population: int  # verdicts of the kind the sample was drawn from
    drawn: int
    right: int = 0
    wrong: int = 0

    @property
    def unmarked(self) -> int:
        return self.drawn - self.right - self.wrong

    @property
    def share(self) -> float | None:
        marked = self.right + self.wrong
        return self.right / marked if marked else None


def verdicts(lines: Iterable[str]) -> list[Verdict]:
    return [Verdict.model_validate(json.loads(line)) for line in lines if line.strip()]


def draw(found: Sequence[Verdict], per_kind: int, seed: int) -> dict[str, list[Verdict]]:
    """`per_kind` verdicts of each kind, or every one where fewer exist."""
    rng = random.Random(seed)
    drawn: dict[str, list[Verdict]] = {}
    # sorted first: one seed then draws the same lines from any input order
    for kind in sorted({one.kind for one in found}):
        pool = sorted((one for one in found if one.kind == kind), key=lambda one: one.id)
        drawn[kind] = sorted(rng.sample(pool, min(per_kind, len(pool))), key=lambda one: one.id)
    return drawn


def sheet(found: Sequence[Verdict], per_kind: int, seed: int) -> str:
    out = [
        "# Spot check",
        "",
        f"Drawn with seed {seed}, {per_kind} per kind. Mark each line `[y]` where the",
        "judge's verdict is right and `[n]` where it is wrong.",
        "",
    ]
    for kind, lines in draw(found, per_kind, seed).items():
        population = sum(one.kind == kind for one in found)
        out += [f"## {kind}: {len(lines)} of {population}", ""]
        # one line per verdict, or the reader would split a mark from its line
        out += [
            f"{n}. [ ] `{one.id}` {' '.join(one.text.split())}"
            for n, one in enumerate(lines, start=1)
        ]
        out.append("")
    return "\n".join(out)


def read(text: str) -> list[Precision]:
    """Each kind's precision from a marked sheet. A mark other than `y` or
    `n` is refused: read as unmarked, it would shrink the denominator."""
    rows: list[Precision] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if heading := _HEADING.match(line):
            rows.append(
                Precision(
                    kind=heading["kind"],
                    population=int(heading["population"]),
                    drawn=int(heading["drawn"]),
                )
            )
        elif (marked := _LINE.match(line)) and rows:
            mark = marked["mark"].lower()
            if mark == " ":
                continue
            if mark not in MARKS:
                raise ValueError(f"line {number}: mark {marked['mark']!r} is neither y nor n")
            if MARKS[mark]:
                rows[-1].right += 1
            else:
                rows[-1].wrong += 1
    return rows
