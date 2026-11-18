"""The diagnosis call over failed attempts and over labelled mutants: `log.md`,
Diagnoses."""

import hashlib
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime

from climb.calls import CallLog, Transport
from climb.diagnoser import DEFAULT, Reading, Task, diagnose, request_hash
from climb.diagnosing.tasks import Tasks
from climb.ids import new_id
from climb.judging.labelled import LabelledMutant
from climb.log import AttemptLog
from climb.mutant_diagnoses import MutantDiagnosisLog
from climb.runs import CONCURRENCY, Bounded, as_answered
from climb.schema import (
    Attempt,
    Call,
    Configuration,
    Diagnosis,
    MachineProvenance,
    MutantDiagnosis,
)

# labelled mutants read per operator by default; constants alone are over half
SAMPLE = 20


@dataclass
class Result:
    diagnosed: int = 0
    unanswered: int = 0  # a refusal or a reply cut short: no record, the call logged
    failed: list[str] = field(default_factory=list[str])
    skipped: int = 0  # answered already at this configuration and prompt
    aborted: bool = False

    @property
    def written(self) -> int:
        return self.diagnosed


def code_hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()[:12]


def sample(
    mutants: Sequence[LabelledMutant], per_operator: int | None = SAMPLE
) -> list[LabelledMutant]:
    """The first `per_operator` of each operator, in the set's own order, so two
    configurations read the same mutants."""
    if per_operator is None:
        return list(mutants)
    taken: dict[str, int] = {}
    kept: list[LabelledMutant] = []
    for one in mutants:
        if taken.get(one.operator, 0) < per_operator:
            taken[one.operator] = taken.get(one.operator, 0) + 1
            kept.append(one)
    return kept


def diagnose_attempts(
    transport: Transport,
    log: AttemptLog,
    calls: CallLog,
    tasks: Tasks,
    *,
    user_id: str | None = None,
    configuration: Configuration = DEFAULT,
    limit: int | None = None,
    concurrency: int = CONCURRENCY,
    fresh: bool = False,
) -> Result:
    """Every failed attempt with code, but those already read at this
    configuration and prompt."""
    failed = [
        one
        for one in log.attempts(user_id)
        if not one.solved and one.code and one.problem_id in tasks.problems
    ]
    read = log.diagnoses(user_id)

    def done(attempt: Attempt) -> bool:
        asked = request_hash(tasks.attempt(attempt), attempt.code or "")
        return any(
            one.attempt_id == attempt.id and one.at_configuration(configuration, asked)
            for one in read
        )

    def store(attempt: Attempt, reading: Reading, call: Call) -> None:
        log.append_diagnosis(
            Diagnosis(
                id=new_id(),
                created_at=datetime.now(UTC),
                attempt_id=attempt.id,
                cause=reading.cause,
                evidence=reading.evidence,
                **MachineProvenance.of(call).model_dump(),
            )
        )

    return _run(
        transport,
        calls,
        failed,
        task=tasks.attempt,
        code=lambda one: one.code or "",
        name=lambda one: one.id,
        done=done,
        store=store,
        configuration=configuration,
        limit=limit,
        concurrency=concurrency,
        fresh=fresh,
    )


def diagnose_mutants(
    transport: Transport,
    log: MutantDiagnosisLog,
    calls: CallLog,
    mutants: Sequence[LabelledMutant],
    tasks: Tasks,
    *,
    configuration: Configuration = DEFAULT,
    limit: int | None = None,
    concurrency: int = CONCURRENCY,
    fresh: bool = False,
) -> Result:
    """Each labelled mutant whose template is still seeded, but those already
    read at this configuration and prompt."""
    reading = (
        [one for one in mutants if one.template_id in tasks.templates]
        if tasks.reads_mutants
        else []
    )
    read = log.all()

    def key(one: LabelledMutant) -> tuple[str, str, str]:
        return one.template_id, one.form_digest, code_hash(one.code)

    def done(one: LabelledMutant) -> bool:
        asked = request_hash(tasks.mutant(one), one.code)
        return any(
            (stored.template_id, stored.form_digest, stored.code_hash) == key(one)
            and stored.at_configuration(configuration, asked)
            for stored in read
        )

    def store(one: LabelledMutant, reading: Reading, call: Call) -> None:
        log.append(
            MutantDiagnosis(
                id=new_id(),
                created_at=datetime.now(UTC),
                template_id=one.template_id,
                form_digest=one.form_digest,
                code_hash=code_hash(one.code),
                cause=reading.cause,
                evidence=reading.evidence,
                **MachineProvenance.of(call).model_dump(),
            )
        )

    return _run(
        transport,
        calls,
        reading,
        task=tasks.mutant,
        code=lambda one: one.code,
        name=lambda one: f"{one.template_id}:{one.line}:{one.change}",
        done=done,
        store=store,
        configuration=configuration,
        limit=limit,
        concurrency=concurrency,
        fresh=fresh,
    )


def _run[T](
    transport: Transport,
    calls: CallLog,
    items: Sequence[T],
    *,
    task: Callable[[T], Task],
    code: Callable[[T], str],
    name: Callable[[T], str],
    done: Callable[[T], bool],
    store: Callable[[T, Reading, Call], None],
    configuration: Configuration,
    limit: int | None,
    concurrency: int,
    fresh: bool,
) -> Result:
    result = Result()
    asking = [one for one in items if fresh or not done(one)]
    result.skipped = len(items) - len(asking)
    asking = asking[:limit]
    answers = Bounded(
        as_answered(
            lambda one: diagnose(
                transport, calls, task(one), code(one), configuration=configuration
            ),
            asking,
            concurrency=concurrency,
        )
    )
    # records are written here, on the calling thread: each log has one writer
    for _, item, answer, failure in answers:
        if failure is not None or answer is None:
            result.failed.append(f"{name(item)}: {failure!r}")
            continue
        reading, call = answer
        if reading is None:
            result.unanswered += 1
            continue
        store(item, reading, call)
        result.diagnosed += 1
    result.aborted = answers.aborted
    return result
