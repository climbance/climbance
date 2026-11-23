"""The labelled mutants the diagnosis call is scored against:
`cli/diagnoser.md`."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from climb.judging.keylines import filled_in
from climb.mutation import Operator, operator_of
from climb.schema import (
    CaseOutcome,
    FailureMode,
    ItemStatus,
    JudgementItem,
    KeyLineChoice,
    KeyLineItem,
)


@dataclass(frozen=True)
class LabelledMutant:
    template_id: str
    form_digest: str
    code: str  # as an item shows it: no comments, no harness
    line: int
    change: str
    operator: Operator
    mode: FailureMode
    case_args: list[Any]
    case_expected: Any
    outcome: CaseOutcome
    returned: Any
    # a slip mutant's problem, whose canonical was mutated; absent on a form's
    problem_id: str | None = None


def labelled_mutants(
    judged: Sequence[JudgementItem], keyed: Sequence[KeyLineItem]
) -> list[LabelledMutant]:
    """One per distinct mutant the served items carry."""
    found: dict[tuple[str, str, str], LabelledMutant] = {}
    for item in judged:
        if item.clean or item.status is not ItemStatus.SERVED:
            continue
        assert item.line is not None
        _keep(found, item, item.code, item.line, item)
    for item in keyed:
        if item.status is not ItemStatus.SERVED:
            continue
        for choice in item.choices:
            if not choice.correct:
                _keep(found, item, filled_in(item, choice.text), item.line, choice)
    return sorted(found.values(), key=lambda one: (one.template_id, one.line, one.change))


def _keep(
    found: dict[tuple[str, str, str], LabelledMutant],
    item: JudgementItem | KeyLineItem,
    code: str,
    line: int,
    flaw: JudgementItem | KeyLineChoice,
) -> None:
    # each item's own validator guarantees a flaw names these
    assert flaw.change is not None and flaw.case_args is not None and flaw.outcome
    # a mutant served by both exercises is one mistake, counted once
    found.setdefault(
        (item.template_id, item.form_digest, code),
        LabelledMutant(
            template_id=item.template_id,
            form_digest=item.form_digest,
            code=code,
            line=line,
            change=flaw.change,
            operator=operator_of(flaw.change),
            mode=FailureMode.RUST,
            case_args=flaw.case_args,
            case_expected=flaw.case_expected,
            outcome=flaw.outcome,
            returned=flaw.returned,
        ),
    )
