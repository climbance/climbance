"""Rule 35: a trace item's failed run and its corrected run, replayed in the
scripted environment, give the stored results, and only the corrected run
reaches the goal."""

import concurrent.futures as cf
import json
from typing import Any

from climb.knowledge.authoring.course import Course, Report
from climb.knowledge.authoring.drills import of_format
from climb.knowledge.authoring.execution import Ran, Runs
from climb.knowledge.files import result_shown

ENVIRONMENTS = "environments"

# the environment, then each step replayed; the final answer is the last message
REPLAY = """\
{environment}


import json as _json

_env = Environment()
_answer = None
_results = []
for _step in _json.loads({steps!r}):
    if "call" in _step:
        if _step["call"] not in TOOLS:
            raise NameError(f"no tool {{_step['call']}} in the environment")
        _results.append(getattr(_env, _step["call"])(**_step.get("args", {{}})))
        _answer = None
    else:
        _answer = _step.get("say")
print(_json.dumps([_results, bool(_env.goal(_answer)), _env.state()], default=repr))
"""


def replay(environment: str, steps: list[dict[str, Any]]) -> str:
    return REPLAY.format(environment=environment.strip("\n"), steps=json.dumps(steps))


def traced(course: Course, report: Report, pool: cf.Executor, runs: Runs) -> int:
    jobs: dict[cf.Future[Ran], tuple[dict[str, Any], list[dict[str, Any]], bool]] = {}
    for raw in of_format(course, "trace"):
        where = f"{raw['_file']} {raw.get('id', '?')}"
        path = course.root / ENVIRONMENTS / f"{raw.get('environment')}.py"
        if not path.is_file():
            report.error(35, where, f"no environment {ENVIRONMENTS}/{path.name}")
            continue
        failed: list[dict[str, Any]] = raw.get("step", [])
        corrected = failed[: int(raw.get("k", 1)) - 1] + raw.get("corrected", [])
        for steps, fixed in ((failed, False), (corrected, True)):
            jobs[pool.submit(runs.run, replay(path.read_text(), steps))] = (raw, steps, fixed)
    for future in cf.as_completed(jobs):
        raw, steps, fixed = jobs[future]
        if problem := _unreplayed(raw, steps, fixed, *future.result()):
            run = "the corrected run" if fixed else "the failed run"
            report.error(35, f"{raw['_file']} {raw.get('id', '?')}", f"{run}: {problem}")
    return len(jobs)


def _unreplayed(
    raw: dict[str, Any], steps: list[dict[str, Any]], fixed: bool, status: int, out: str, err: str
) -> str | None:
    if status:
        return f"the replay raises: {err.strip().splitlines()[-1:]}"
    results, reached, state = json.loads(out.strip("\n").splitlines()[-1])
    stored = [step.get("result") for step in steps if "call" in step]
    for n, (got, held) in enumerate(zip(results, stored, strict=True), 1):
        if json.loads(json.dumps(held, default=repr)) != got:
            return f"call {n} returns {result_shown(got)}, where the item stores {held!r}"
    if reached != fixed:
        return "reaches the goal" if reached else "misses the goal"
    key = "corrected_end_state" if fixed else "end_state"
    if state != raw.get(key):
        return f"the environment ends {state!r}, where the item stores {raw.get(key)!r}"
    return None
