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
        if malformed(concept.get("checks", [])):
            report.error(31, at, "a check is not { model, checked_on, holds, measured }")
            continue
        standing(report, at, concept.get("checks", []), panel, every, today)
    for name, why in course.retired.items():
        if not isinstance(why.get("retired_on"), date) or not why.get("because"):
            report.error(31, f"check.toml retired {name}", "needs retired_on and because")


def standing(
    report: Report,
    at: str,
    checks: list[dict[str, Any]],
    panel: list[str],
    every: int,
    today: date,
    rule: int = 31,
) -> None:
    last, owed = latest(checks), due(checks, panel, every, today)
    for model in panel:
        if model not in last:
            report.warn(rule, at, f"due: never checked on {model}")
        elif not last[model]["holds"]:
            on = last[model]["checked_on"]
            report.error(rule, at, f"stopped holding on {model} on {on}: retire it")
        elif model in owed:
            report.warn(rule, at, f"due: last checked on {model} on {last[model]['checked_on']}")


def malformed(checks: object) -> bool:
    """Not a list of `{ model, checked_on, holds, measured }`."""
    if not isinstance(checks, list):
        return True
    return any(
        not isinstance(one, dict)
        or any(not isinstance(cast(dict[str, Any], one).get(k), t) for k, t in CHECK.items())
        for one in cast(list[object], checks)
    )


def latest(checks: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """The latest check on each model: its standing on that model."""
    found: dict[str, dict[str, Any]] = {}
    for one in checks:
        held = found.get(one["model"])
        if held is None or held["checked_on"] <= one["checked_on"]:
            found[one["model"]] = one
    return found


def due(checks: list[dict[str, Any]], panel: list[str], every: int, today: date) -> list[str]:
    """The panel models with no check, or whose latest held and is past due.
    A failed latest check is not due: the claim is retired, not run again."""
    last = latest(checks)
    return [
        m
        for m in panel
        if m not in last
        or (last[m]["holds"] and last[m]["checked_on"] + timedelta(days=every) < today)
    ]
