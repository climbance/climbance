"""The diagnosed cause the pick reads: `api/pick.md`."""

from collections.abc import Mapping, Sequence

from climb.diagnoser import MEASURED, request_hash, system_digest
from climb.diagnosing.tasks import Tasks
from climb.schema import Attempt, Cause, Diagnosis, Problem, Template


def measured_causes(
    problems: Mapping[str, Problem],
    templates: Mapping[str, Template],
    attempts: Sequence[Attempt],
    diagnoses: Sequence[Diagnosis],
) -> dict[str, Cause]:
    """Each attempt's latest diagnosis by a measured configuration, at the
    baseline prompt: a tool's column is measured apart."""
    trusted = [one for one, digest in MEASURED.items() if digest == system_digest()]
    named = {one.attempt_id for one in diagnoses}
    tasks = Tasks(problems, templates)
    asked = {
        one.id: request_hash(tasks.attempt(one), one.code or "")
        for one in attempts
        if one.id in named and one.problem_id in problems
    }
    return {
        one.attempt_id: one.cause
        for one in diagnoses
        if one.attempt_id in asked
        and any(one.at_configuration(each, asked[one.attempt_id]) for each in trusted)
    }
