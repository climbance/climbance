"""`climb module reverify` on a prompt artefact: each side sent to a panel
model `samples` times, the answers scored by the artefact's `check`, and the
file of samples and checks rewritten. `content-repo/ai-drills.md`"""

import json
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from climb.knowledge.authoring.course import Course
from climb.knowledge.authoring.model_checks import due, malformed
from climb.knowledge.authoring.sampling import prompted, shares, stored
from climb.knowledge.files import CLEAN, SAMPLES

# a model and a prompt to the call's id and its answer
type Answer = Callable[[str, str], tuple[str, str]]

HEAD = "# Written by `climb module reverify`: rule 36 in the engine repo.\n"


@dataclass(frozen=True)
class Sample:
    side: str
    model: str
    call: str
    text: str
    passed: bool


def sent(lines: str, given: str) -> str:
    """The prompt a side's lines make, the `input` in place of `{input}`."""
    return lines.strip("\n").replace("{input}", given)


def owed(course: Course, today: date) -> dict[str, list[str]]:
    """Each prompt artefact, and the panel models it is due on."""
    panel = course.models.get("panel", [])
    every = course.models.get("every_days", 0)
    found: dict[str, list[str]] = {}
    for raw in prompted(course):
        checks = stored(course, raw).get("checks", [])
        if not malformed(checks) and (models := due(checks, panel, every, today)):
            found[raw["id"]] = models
    return found


def asked(raw: dict[str, Any], model: str, answer: Answer) -> tuple[list[Sample], bool, str]:
    """Every side's samples on one model, whether each side met its share, and
    the counts as a line."""
    namespace: dict[str, Any] = {"__name__": "__main__"}
    # in-process, as a claim's witness is: the check is authored content
    exec(raw["check"], namespace)
    sides = {CLEAN: raw["lines"], **{v["id"]: v["lines"] for v in raw.get("variant", [])}}
    samples: list[Sample] = []
    counts: list[str] = []
    holds = True
    for side, lines in sides.items():
        mine: list[Sample] = []
        for _ in range(int(raw["samples"])):
            call, text = answer(model, sent(lines, raw["input"]))
            mine.append(Sample(side, model, call, text, bool(namespace["check"](text))))
        right = [one for one in mine if one.passed == (side == CLEAN)]
        holds = holds and len(right) >= shares(raw)[side] * len(mine)
        counts.append(
            f"{side} {len(right)} of {len(mine)} {'passed' if side == CLEAN else 'failed'}"
        )
        # a queue shows a side's first answer: one bearing out the key
        samples += right + [one for one in mine if one not in right]
    return samples, holds, "; ".join(counts)


def recorded(
    course: Course, raw: dict[str, Any], samples: list[Sample], check: dict[str, Any]
) -> None:
    """The model's samples, where the file holds none from it yet, and the
    check, appended; the file rewritten whole."""
    held = stored(course, raw)
    kept: list[dict[str, Any]] = held.get("sample", [])
    if not any(one.get("model") == check["model"] for one in kept):
        kept = kept + [vars(one) for one in samples]
    checks = [*held.get("checks", []), check]
    path = _path(course, raw)
    path.parent.mkdir(exist_ok=True)
    path.write_text(
        HEAD
        + "".join(_table("sample", one) for one in kept)
        + "".join(_table("checks", one) for one in checks)
    )
    if tomllib.loads(path.read_text()) != {"sample": kept, "checks": checks}:
        raise ValueError(f"{path}: the samples did not land as written")


def _table(name: str, fields: dict[str, Any]) -> str:
    return f"\n[[{name}]]\n" + "".join(f"{key} = {_value(v)}\n" for key, v in fields.items())


def _value(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, date):
        return value.isoformat()
    # a JSON string is a TOML basic string
    return json.dumps(value)


def _path(course: Course, raw: dict[str, Any]) -> Path:
    return course.root / SAMPLES / f"{raw['id']}.toml"
