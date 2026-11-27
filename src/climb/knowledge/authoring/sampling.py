"""Rule 36: a prompt artefact's stored answers are what its `check` says of
them, each side meets its share on each model, and its latest re-check on each
panel model held."""

import concurrent.futures as cf
import json
import tomllib
from collections.abc import Iterator
from datetime import date
from typing import Any

from climb.knowledge.authoring.course import Course, Report
from climb.knowledge.authoring.drills import of_format
from climb.knowledge.authoring.execution import Ran, Runs
from climb.knowledge.authoring.model_checks import malformed, standing
from climb.knowledge.files import CLEAN, SAMPLES

VERDICTS = """\
{check}


import json as _json

print(_json.dumps([bool(check(_text)) for _text in _json.loads({texts!r})]))
"""


def prompted(course: Course) -> list[dict[str, Any]]:
    return [raw for raw in of_format(course, "judge") if "share" in raw]


def stored(course: Course, raw: dict[str, Any]) -> dict[str, Any]:
    path = course.root / SAMPLES / f"{raw.get('id')}.toml"
    return tomllib.loads(path.read_text()) if path.is_file() else {}


def verdicts(check: str, texts: list[str]) -> str:
    return VERDICTS.format(check=check.strip("\n"), texts=json.dumps(texts))


def sampled(
    course: Course, report: Report, pool: cf.Executor, runs: Runs, today: date | None = None
) -> int:
    jobs: dict[cf.Future[Ran], tuple[dict[str, Any], list[dict[str, Any]]]] = {}
    for raw in prompted(course):
        held = stored(course, raw)
        where = f"{raw['_file']} {raw.get('id', '?')}"
        if malformed(held.get("checks", [])):
            report.error(36, where, "a check is not { model, checked_on, holds, measured }")
        else:
            panel, every = course.models.get("panel", []), course.models.get("every_days", 0)
            standing(report, where, held.get("checks", []), panel, every, today or date.today(), 36)
        if not (samples := held.get("sample", [])):
            report.error(36, where, f"no samples in {SAMPLES}/: run climb module reverify")
        else:
            texts = [str(one.get("text")) for one in samples]
            jobs[pool.submit(runs.run, verdicts(raw.get("check", ""), texts))] = (raw, samples)
    for future in cf.as_completed(jobs):
        raw, samples = jobs[future]
        for problem in _unmet(raw, samples, *future.result()):
            report.error(36, f"{raw['_file']} {raw.get('id', '?')}", problem)
    return len(jobs)


def shares(raw: dict[str, Any]) -> dict[str, float]:
    """Each side's share: the clean lines' passing, a variant's failing."""
    return {CLEAN: raw["share"], **{v.get("id"): v.get("share", 1) for v in raw.get("variant", [])}}


def met(raw: dict[str, Any], samples: list[dict[str, Any]]) -> dict[str, list[str]]:
    """The sides under their share, by model, read from each `passed`."""
    under: dict[str, list[str]] = {}
    for model in dict.fromkeys(one.get("model") for one in samples):
        for side, share in shares(raw).items():
            mine = [
                one["passed"] for one in samples if (one["model"], one["side"]) == (model, side)
            ]
            right = sum(mine) if side == CLEAN else len(mine) - sum(mine)
            if not mine or right < share * len(mine):
                under.setdefault(str(model), []).append(f"{side} {right} of {len(mine)}")
    return under


def _unmet(
    raw: dict[str, Any], samples: list[dict[str, Any]], status: int, out: str, err: str
) -> Iterator[str]:
    if status:
        yield f"the check raises: {err.strip().splitlines()[-1:]}"
        return
    for n, (one, passed) in enumerate(
        zip(samples, json.loads(out.strip().splitlines()[-1]), strict=True), 1
    ):
        if one.get("passed") is not passed:
            held = one.get("passed")
            yield f"sample {n} on {one.get('model')}: the check says {passed}, the file {held}"
            return
    for model, sides in met(raw, samples).items():
        yield f"under its share on {model}: {', '.join(sides)}"
