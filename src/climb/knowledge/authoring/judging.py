"""Rule 34: a spot-the-flaw artefact's clean lines pass its `check` on its
`input`, each variant's fail it, and each stored output is what the lines
gave."""

import concurrent.futures as cf
import json
from typing import Any

from climb.knowledge.authoring.course import Course, Report
from climb.knowledge.authoring.drills import of_format
from climb.knowledge.authoring.execution import Ran, Runs

# the artefact, then the check, then the call; the output as its repr
WITNESS = """\
{lines}


{check}


import json as _json

_output = {input}
print(_json.dumps([repr(_output), bool(check(_output))]))
"""


def witness(lines: str, raw: dict[str, Any]) -> str:
    return WITNESS.format(
        lines=lines.strip("\n"), check=raw["check"].strip("\n"), input=raw["input"]
    )


def judged(course: Course, report: Report, pool: cf.Executor, runs: Runs) -> int:
    jobs: dict[cf.Future[Ran], tuple[dict[str, Any], dict[str, Any] | None]] = {}
    for raw in of_format(course, "judge"):
        if not {"lines", "check", "input"} <= raw.keys():
            continue
        jobs[pool.submit(runs.run, witness(raw["lines"], raw))] = (raw, None)
        for variant in raw.get("variant", []):
            jobs[pool.submit(runs.run, witness(variant.get("lines", ""), raw))] = (raw, variant)
    for future in cf.as_completed(jobs):
        raw, variant = jobs[future]
        where = raw.get("id", "?") + (f" variant {variant.get('id', '?')}" if variant else "")
        if problem := _unproven(variant or raw, variant is None, *future.result()):
            report.error(34, f"{raw['_file']} {where}", problem)
    return len(jobs)


def _unproven(held: dict[str, Any], clean: bool, status: int, out: str, err: str) -> str | None:
    if status:
        return f"the witness raises: {err.strip().splitlines()[-1:]}"
    output, passed = json.loads(out.strip("\n").splitlines()[-1])
    if passed != clean:
        return "the clean lines fail the check" if clean else "the variant passes the check"
    if output != held.get("output"):
        return f"the lines give {output}, where the item stores {held.get('output')!r}"
    return None
