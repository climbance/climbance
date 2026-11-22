"""The diagnosis call scored per label mode: `cli/diagnoser.md`."""

from collections.abc import Sequence
from dataclasses import dataclass

from climb.diagnoser import request_hash
from climb.diagnosing.run import code_hash
from climb.diagnosing.tasks import Tasks
from climb.judging.labelled import LabelledMutant
from climb.mutation import Operator
from climb.schema import (
    IMPLIED,
    Attempt,
    Cause,
    Configuration,
    Diagnosis,
    FailureMode,
    MachineProvenance,
    MutantDiagnosis,
    SelfLabel,
)
from climb.scorer import agreement
from climb.scorer.spot import Verdict

# under this many verdicts a share swings on one of them, so none is shown
MINIMUM = 10


@dataclass(frozen=True)
class Row:
    label: str
    implied: Cause
    read: int  # verdicts this configuration wrote on the row
    matched: int

    @property
    def share(self) -> float | None:
        return self.matched / self.read if self.read >= MINIMUM else None


def scored(
    configuration: Configuration,
    tasks: Tasks,
    attempts: Sequence[Attempt],
    labels: Sequence[SelfLabel],
    diagnoses: Sequence[Diagnosis],
    mutants: Sequence[LabelledMutant],
    mutant_diagnoses: Sequence[MutantDiagnosis],
) -> list[Row]:
    """One row per self-label mode, then the mutants whole and per operator.
    A verdict counts where it answers the prompt this tool set would send."""
    mode = {one.attempt_id: one.mode for one in labels}  # in landing order: the latest wins
    cause = {
        one: found.cause
        for one, found in _latest(configuration, tasks, attempts, diagnoses).items()
    }
    rows = [
        _row(
            labelled.value,
            IMPLIED[labelled],
            {one: cause[one] for one, named in mode.items() if named is labelled and one in cause},
        )
        for labelled in (FailureMode.SYNTAX, FailureMode.GAP, FailureMode.RUST)
    ]
    verdicts: dict[tuple[str, str, str, str], Cause] = {
        (one.template_id, one.form_digest, one.code_hash, one.prompt_hash or ""): one.cause
        for one in mutant_diagnoses
        if written_by(one, configuration)
    }
    read = [
        (one, verdicts[key])
        for one in mutants
        if tasks.reads_mutants
        and one.template_id in tasks.templates
        and (key := (*_key(one), request_hash(tasks.mutant(one), one.code))) in verdicts
    ]
    implied = IMPLIED[FailureMode.RUST]
    rows.append(_row("mutants", implied, {_id(one): found for one, found in read}))
    for operator in [one for one in Operator if any(m.operator is one for m in mutants)]:
        named = {_id(one): found for one, found in read if one.operator is operator}
        rows.append(_row(f"  {operator}", implied, named))
    return rows


def unscored(
    configuration: Configuration,
    tasks: Tasks,
    attempts: Sequence[Attempt],
    labels: Sequence[SelfLabel],
    diagnoses: Sequence[Diagnosis],
) -> list[Verdict]:
    """The latest verdicts no self-label scores, for the spot check. A `speed`
    or `none` label implies no cause, so its attempt stays in."""
    mode = {one.attempt_id: one.mode for one in labels}
    scored_ids = {one for one, named in mode.items() if named in IMPLIED}
    by_id = {one.id: one for one in attempts}
    return [
        Verdict(
            id=attempt_id,
            kind=found.cause.value,
            # fenced: a statement ends on the signature the code opens with
            text=f"{tasks.problems[by_id[attempt_id].problem_id].statement}\n\n"
            f"```python\n{by_id[attempt_id].code or ''}\n```",
        )
        for attempt_id, found in _latest(configuration, tasks, attempts, diagnoses).items()
        if attempt_id not in scored_ids
    ]


def _latest(
    configuration: Configuration,
    tasks: Tasks,
    attempts: Sequence[Attempt],
    diagnoses: Sequence[Diagnosis],
) -> dict[str, Diagnosis]:
    """Each attempt's latest diagnosis at the prompt this tool set sends."""
    asked = {
        one.id: request_hash(tasks.attempt(one), one.code or "")
        for one in attempts
        if one.problem_id in tasks.problems
    }
    return {
        one.attempt_id: one
        for one in diagnoses
        if one.attempt_id in asked and one.at_configuration(configuration, asked[one.attempt_id])
    }


def written_by(record: MachineProvenance, configuration: Configuration) -> bool:
    return (record.model, record.effort, record.pin, record.temperature) == (
        configuration.model,
        configuration.effort,
        configuration.pin,
        configuration.temperature,
    )


def _key(one: LabelledMutant) -> tuple[str, str, str]:
    return one.template_id, one.form_digest, code_hash(one.code)


def _id(one: LabelledMutant) -> str:
    return "/".join(_key(one))


def _row(label: str, implied: Cause, causes: dict[str, Cause]) -> Row:
    result = agreement({one: [implied] for one in causes}, {k: [v] for k, v in causes.items()})
    return Row(label, implied, result.scored, result.exact)
