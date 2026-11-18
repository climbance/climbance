"""What the diagnosis call is told about each item, under a tool set. The run
and the score build each prompt here, so a stored verdict is matched on the
prompt hash it was written under."""

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from climb.diagnoser import Task, Tool
from climb.judging.labelled import LabelledMutant
from climb.schema import (
    Attempt,
    AttemptVerification,
    CaseOutcome,
    Problem,
    Template,
    TestCase,
)

# a stored case may weigh up to 1 MiB; the call reads its head
CLIPPED = 2000


def named(template: Template) -> str:
    """The form as the call is told it: its name, never its code."""
    return f"{template.title}: {template.trigger}"


def clip(text: str) -> str:
    return text if len(text) <= CLIPPED else text[:CLIPPED] + " …"


def rendered(
    args: list[Any],
    expected: object,
    outcome: CaseOutcome,
    returned: str | None,
    error: str | None,
) -> str:
    """One failed case as the divergence tool shows it. `returned` is JSON."""
    got = {
        CaseOutcome.WRONG: f"returned: {clip(returned or 'null')}",
        CaseOutcome.TIMEOUT: "timed out",
        CaseOutcome.CRASHED: f"raised: {clip(error)}" if error else "crashed",
    }[outcome]
    return "\n".join(
        [f"arguments: {clip(json.dumps(args))}", f"expected: {clip(json.dumps(expected))}", got]
    )


@dataclass(frozen=True)
class Tasks:
    problems: Mapping[str, Problem]
    templates: Mapping[str, Template]
    tools: frozenset[Tool] = frozenset()
    cases: Mapping[str, TestCase] = field(default_factory=dict[str, TestCase])
    runs: Mapping[str, AttemptVerification] = field(
        default_factory=dict[str, AttemptVerification]
    )  # the latest run per attempt

    def attempt(self, attempt: Attempt) -> Task:
        problem = self.problems[attempt.problem_id]
        template = self.templates.get(problem.target_template_id or "")
        return Task(
            statement=problem.statement,
            form=named(template) if template else None,
            failed=self._first_failed(attempt) if Tool.DIVERGENCE in self.tools else None,
            form_code=template.code if template and Tool.FORM_CODE in self.tools else None,
        )

    @property
    def reads_mutants(self) -> bool:
        """Beside a mutant the form's code gives the fault away."""
        return Tool.FORM_CODE not in self.tools

    def mutant(self, mutant: LabelledMutant) -> Task:
        template = self.templates[mutant.template_id]
        failed = rendered(
            mutant.case_args,
            mutant.case_expected,
            mutant.outcome,
            json.dumps(mutant.returned),
            None,
        )
        return Task(
            statement=f"Implement {template.title}.",
            form=named(template),
            failed=failed if Tool.DIVERGENCE in self.tools else None,
        )

    def _first_failed(self, attempt: Attempt) -> str | None:
        run = self.runs.get(attempt.id)
        for result in run.results if run else []:
            case = self.cases.get(result.case_id)
            if result.outcome is not CaseOutcome.PASSED and case is not None:
                return rendered(
                    case.args, case.expected, result.outcome, result.returned, result.error
                )
        return None
