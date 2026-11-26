"""Rule 31: a claim that depends on a model is checked on the module's panel,
again on a schedule, and retired once it stops holding."""

from datetime import date, timedelta
from typing import Any, cast

from climb.knowledge.authoring.course import Course, Report

CHECK = {"model": str, "checked_on": date, "holds": bool, "measured": str}


def checked(course: Course, report: Report, today: date | None = None) -> None:
    today = today or date.today()
    panel = course.models.get("panel", [])
    every = course.models.get("every_days")
    for name, concept in course.concepts.items():
        at = f"{concept['_file']} {name}"
        if name in course.retired:
            report.error(31, at, "the id was retired")
        if "model_witness" not in concept:
            if "checks" in concept:
                report.error(31, at, "checks with no model_witness")
            continue
        if not panel or not isinstance(every, int):
            report.error(31, at, "check.toml names no [models] panel and every_days")
            continue
        latest = _latest(report, at, concept.get("checks"))
        for model in panel:
            last = latest.get(model)
            if last is None:
                report.warn(31, at, f"due: never checked on {model}")
            elif not last["holds"]:
                report.error(
                    31, at, f"stopped holding on {model} on {last['checked_on']}: retire it"
                )
            elif last["checked_on"] + timedelta(days=every) < today:
                report.warn(31, at, f"due: last checked on {model} on {last['checked_on']}")
    for name, why in course.retired.items():
        if not isinstance(why.get("retired_on"), date) or not why.get("because"):
            report.error(31, f"check.toml retired {name}", "needs retired_on and because")


def _latest(report: Report, at: str, checks: object) -> dict[str, dict[str, Any]]:
    if not isinstance(checks, list):
        report.error(31, at, "a model_witness with no checks list")
        return {}
    latest: dict[str, dict[str, Any]] = {}
    for one in cast(list[object], checks):
        if not isinstance(one, dict) or any(
            not isinstance(cast(dict[str, Any], one).get(k), t) for k, t in CHECK.items()
        ):
            report.error(31, at, "a check is not { model, checked_on, holds, measured }")
            continue
        found = cast(dict[str, Any], one)
        held = latest.get(found["model"])
        if held is None or held["checked_on"] <= found["checked_on"]:
            latest[found["model"]] = found
    return latest
