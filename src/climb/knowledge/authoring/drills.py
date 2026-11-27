"""Rules 32 and 33: an estimate drill's key and working are what its `compute`
prints, and a pick-the-metric drill's scores are what the module's metric
library and its `utility` give on its outputs."""

import concurrent.futures as cf
import json
import math
import tomllib
from typing import Any, cast

from climb.knowledge.authoring.course import Course, Report
from climb.knowledge.authoring.execution import Ran, Runs

# the given values, the two texts, and `tokens` counting by the given tokenizer
PREAMBLE = """\
import json as _json
globals().update(_json.loads({given!r}))
sent = {sent!r}
received = {received!r}


def tokens(text):
    import tiktoken

    return len(tiktoken.get_encoding(tokenizer).encode(text))


"""


# the library's functions, then each candidate's pair and the goal's, as JSON
SCORING = """\
{library}

import json as _json

_item = _json.loads({item!r})
expected, a, b = _item["expected"], _item["a"], _item["b"]

{utility}

for _one in _item["candidates"]:
    _metric = globals()[_one["metric"]]
    _params = _one.get("params", {{}})
    print(_json.dumps([_metric(a, expected, **_params), _metric(b, expected, **_params)]))
print(_json.dumps([utility(a, expected), utility(b, expected)]))
"""
LIBRARY = "metrics.py"


def of_format(course: Course, form: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for path in sorted((course.root / "drills").glob("*/*.toml")):
        for raw in tomllib.loads(path.read_text()).get("drill", []):
            if raw.get("format") == form:
                found.append(raw | {"_file": str(path.relative_to(course.root))})
    return found


def program(raw: dict[str, Any]) -> str:
    given = json.dumps({one["name"]: one["value"] for one in raw.get("given", [])})
    head = PREAMBLE.format(given=given, sent=raw.get("sent"), received=raw.get("received"))
    return head + raw["compute"].lstrip("\n")


def drills(course: Course, report: Report, pool: cf.Executor, runs: Runs) -> int:
    items = [raw for raw in of_format(course, "estimate") if "compute" in raw]
    jobs: dict[cf.Future[Ran], dict[str, Any]] = {
        pool.submit(runs.run, program(raw)): raw for raw in items
    }
    for future in cf.as_completed(jobs):
        raw = jobs[future]
        if problem := _mismatch(raw, *future.result()):
            report.error(32, f"{raw['_file']} {raw.get('id', '?')}", problem)
    return len(jobs) + _metrics(course, report, pool, runs)


def scoring(library: str, raw: dict[str, Any]) -> str:
    item = json.dumps({key: raw.get(key) for key in ("expected", "a", "b", "candidates")})
    return SCORING.format(library=library, item=item, utility=raw["utility"].lstrip("\n"))


def _metrics(course: Course, report: Report, pool: cf.Executor, runs: Runs) -> int:
    items = [raw for raw in of_format(course, "metric") if "utility" in raw]
    if not items:
        return 0
    path = course.root / LIBRARY
    if not path.exists():
        report.error(33, LIBRARY, "a pick-the-metric drill needs the module's metric library")
        return 0
    library = path.read_text()
    jobs: dict[cf.Future[Ran], dict[str, Any]] = {
        pool.submit(runs.run, scoring(library, raw)): raw for raw in items
    }
    for future in cf.as_completed(jobs):
        raw = jobs[future]
        if problem := _unscored(raw, *future.result()):
            report.error(33, f"{raw['_file']} {raw.get('id', '?')}", problem)
    return len(jobs)


def _unscored(raw: dict[str, Any], status: int, out: str, err: str) -> str | None:
    if status:
        return f"scoring raises: {err.strip().splitlines()[-1:]}"
    *pairs, goal = [json.loads(line) for line in out.strip("\n").splitlines()]
    held: list[object] = raw.get("scores", [])
    if not _close(goal, raw.get("goal")):
        return f"the goal scores {goal}, where the item stores {raw.get('goal')}"
    if len(pairs) != len(held):
        return f"{len(pairs)} candidates scored, where the item stores {len(held)}"
    for one, got, stored in zip(raw.get("candidates", []), pairs, held, strict=True):
        if not _close(got, stored):
            return f"{one.get('metric')} scores {got}, where the item stores {stored}"
    return None


def _close(got: list[float], held: object) -> bool:
    if not isinstance(held, list):
        return False
    values = [float(one) for one in cast(list[float], held)]
    return len(got) == len(values) and all(
        math.isclose(x, y, rel_tol=1e-9, abs_tol=1e-12) for x, y in zip(got, values, strict=True)
    )


def _mismatch(raw: dict[str, Any], status: int, out: str, err: str) -> str | None:
    if status:
        return f"compute raises: {err.strip().splitlines()[-1:]}"
    lines = out.strip("\n").splitlines()
    if not lines:
        return "compute prints nothing"
    try:
        printed = float(lines[-1])
    except ValueError:
        return f"compute's last line {lines[-1]!r} is no number"
    if not math.isclose(printed, float(raw.get("computed", math.nan)), rel_tol=1e-9):
        return f"compute prints the key {printed!r}, where the item stores {raw.get('computed')!r}"
    if lines[:-1] != raw.get("working"):
        return f"compute prints the working {lines[:-1]!r}, where the item stores another"
    return None
