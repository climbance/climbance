"""The panel and its trials on corpus problems: `corpus.md`, Trials."""

import re
from contextlib import AbstractContextManager, nullcontext
from dataclasses import dataclass
from datetime import UTC, datetime

from climb.calls import CallLog, Transport, ask
from climb.ids import new_id
from climb.runner import runner, verify
from climb.schema import CaseOutcome, Configuration, MachineProvenance, Problem, TestCase, Trial
from climb.schema.case import severest
from climb.sitting import DRILL_CAP_MS


@dataclass(frozen=True)
class Member:
    configuration: Configuration
    max_tokens: int


# weak to strong, as the pilot on the anchors chose them: `corpus.md`
PANEL = (
    Member(
        Configuration(model="meta-llama/llama-3.1-8b-instruct", effort="default", pin="groq"),
        16_000,
    ),
    Member(Configuration(model="openai/gpt-oss-20b", effort="low", pin="coreweave/fp4"), 120_000),
    Member(Configuration(model="openai/gpt-oss-120b", effort="low", pin="coreweave/fp4"), 120_000),
    Member(
        Configuration(model="openai/gpt-oss-120b", effort="medium", pin="coreweave/fp4"), 120_000
    ),
    Member(Configuration(model="openai/gpt-oss-120b", effort="high", pin="coreweave/fp4"), 120_000),
)
TRIES = 3

SYSTEM = (
    "You solve a programming problem. Write Python 3 that defines `solve` with the"
    " signature the statement gives; it is called once per case and returns the"
    " answer. Reply with the code alone, in one ```python code block."
)
FENCE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.S)


def code_in(text: str | None) -> str | None:
    # the last block: a reasoning model may show a draft before its answer
    found = FENCE.findall(text or "")
    return found[-1] if found else None


def trial(
    problem: Problem,
    cases: list[TestCase],
    member: Member,
    try_number: int,
    *,
    transport: Transport,
    calls: CallLog,
    judging: AbstractContextManager[object] | None = None,
) -> Trial:
    """One member's solution, judged as a sitting judges a submission. Hold
    `judging` to time one run at a time: a verdict is wall clock."""
    call, text = ask(
        transport,
        calls,
        system=SYSTEM,
        content=problem.statement,
        configuration=member.configuration,
        max_tokens=member.max_tokens,
    )
    code = code_in(text)
    with judging or nullcontext():
        results = verify(code, cases, cap_ms=DRILL_CAP_MS, stop_early=True) if code else []
    return Trial(
        id=new_id(),
        created_at=datetime.now(UTC),
        problem_id=problem.id,
        try_number=try_number,
        outcome=severest(one.outcome for one in results),
        cases_passed=sum(one.outcome is CaseOutcome.PASSED for one in results),
        cases_run=len(results),
        cap_ms=DRILL_CAP_MS,
        runner=runner(),
        **MachineProvenance.of(call).model_dump(),
    )
