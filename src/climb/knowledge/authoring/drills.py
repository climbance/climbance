"""Rule 32: an estimate drill's key and working are what its `compute` prints
from the numbers it states."""

import concurrent.futures as cf
import json
import math
import tomllib
from typing import Any

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


def estimates(course: Course) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for path in sorted((course.root / "drills").glob("*/*.toml")):
        for raw in tomllib.loads(path.read_text()).get("drill", []):
            if raw.get("format") == "estimate":
                found.append(raw | {"_file": str(path.relative_to(course.root))})
    return found


def program(raw: dict[str, Any]) -> str:
    given = json.dumps({one["name"]: one["value"] for one in raw.get("given", [])})
    head = PREAMBLE.format(given=given, sent=raw.get("sent"), received=raw.get("received"))
    return head + raw["compute"].lstrip("\n")


def drills(course: Course, report: Report, pool: cf.Executor, runs: Runs) -> int:
    items = [raw for raw in estimates(course) if "compute" in raw]
    jobs: dict[cf.Future[Ran], dict[str, Any]] = {
        pool.submit(runs.run, program(raw)): raw for raw in items
    }
    for future in cf.as_completed(jobs):
        raw = jobs[future]
        if problem := _mismatch(raw, *future.result()):
            report.error(32, f"{raw['_file']} {raw.get('id', '?')}", problem)
    return len(jobs)


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
