"""The diagnosis call scored per label mode: `log.md`, Diagnoses."""

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
    asked = {
        one.id: request_hash(tasks.attempt(one), one.code or "")
        for one in attempts
        if one.problem_id in tasks.problems
    }
    mode = {one.attempt_id: one.mode for one in labels}  # in landing order: the latest wins
    cause = {
        one.attempt_id: one.cause
        for one in diagnoses
        if one.attempt_id in asked and one.at_configuration(configuration, asked[one.attempt_id])
    }
    rows = [
        _row(
            labelled.value,
            IMPLIED[labelled],
            [cause[one] for one, named in mode.items() if named is labelled and one in cause],
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
        if one.template_id in tasks.templates
        and (key := (*_key(one), request_hash(tasks.mutant(one), one.code))) in verdicts
    ]
    implied = IMPLIED[FailureMode.RUST]
    rows.append(_row("mutants", implied, [found for _, found in read]))
    for operator in [one for one in Operator if any(m.operator is one for m in mutants)]:
        named = [found for one, found in read if one.operator is operator]
        rows.append(_row(f"  {operator}", implied, named))
    return rows


def written_by(record: MachineProvenance, configuration: Configuration) -> bool:
    return (record.model, record.effort, record.pin, record.temperature) == (
        configuration.model,
        configuration.effort,
        configuration.pin,
        configuration.temperature,
    )


def _key(one: LabelledMutant) -> tuple[str, str, str]:
    return one.template_id, one.form_digest, code_hash(one.code)


def _row(label: str, implied: Cause, causes: list[Cause]) -> Row:
    return Row(label, implied, len(causes), sum(one is implied for one in causes))
