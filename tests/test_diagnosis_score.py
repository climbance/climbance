from dataclasses import replace

from helpers import PROVENANCE_FIELDS, T0, make_problem

from climb.cli.diagnose import cell
from climb.diagnoser import Tool, request_hash
from climb.diagnosing import MINIMUM, Tasks, scored
from climb.diagnosing.run import code_hash
from climb.judging.labelled import LabelledMutant
from climb.mutation import Operator
from climb.schema import (
    Attempt,
    CaseOutcome,
    Cause,
    Configuration,
    Diagnosis,
    FailureMode,
    MutantDiagnosis,
    SelfLabel,
    Template,
)

AT = Configuration(
    model=PROVENANCE_FIELDS["model"],
    effort=PROVENANCE_FIELDS["effort"],
    pin=PROVENANCE_FIELDS["pin"],
    temperature=None,
)
OTHER = AT.model_copy(update={"model": "another-model"})
TEMPLATE = Template(id="t1", slug="largest", title="largest", trigger="the largest", code="x")
TASKS = Tasks(problems={"p1": make_problem("p1")}, templates={"t1": TEMPLATE})


def attempt(id: str) -> Attempt:
    return Attempt(
        id=id, user_id="u-4f9c2a", problem_id="p1", finished_at=T0, solved=False, code=id
    )


def label(attempt_id: str, mode: FailureMode) -> SelfLabel:
    return SelfLabel(id=f"l-{attempt_id}", created_at=T0, attempt_id=attempt_id, mode=mode)


def diagnosis(attempt_id: str, cause: Cause, tasks: Tasks = TASKS) -> Diagnosis:
    asked = request_hash(tasks.attempt(attempt(attempt_id)), attempt_id)
    return Diagnosis(
        id=f"d-{attempt_id}",
        created_at=T0,
        attempt_id=attempt_id,
        cause=cause,
        evidence="a line",
        **PROVENANCE_FIELDS | {"prompt_hash": asked},
    )


def mutant(line: int, operator: Operator) -> LabelledMutant:
    return LabelledMutant(
        template_id="t1",
        form_digest="d1",
        code=f"return {line}\n",
        line=line,
        change="< → <=",
        operator=operator,
        mode=FailureMode.RUST,
        case_args=[1],
        case_expected=1,
        outcome=CaseOutcome.WRONG,
        returned=2,
    )


def verdict(one: LabelledMutant, cause: Cause, tasks: Tasks = TASKS) -> MutantDiagnosis:
    return MutantDiagnosis(
        id=f"m-{one.line}",
        created_at=T0,
        template_id=one.template_id,
        form_digest=one.form_digest,
        code_hash=code_hash(one.code),
        cause=cause,
        evidence="a line",
        **PROVENANCE_FIELDS | {"prompt_hash": request_hash(tasks.mutant(one), one.code)},
    )


def rows(configuration, labels, diagnoses, mutants=(), verdicts=(), tasks=TASKS) -> dict:
    attempts = [attempt(one.attempt_id) for one in labels]
    found = scored(configuration, tasks, attempts, labels, diagnoses, mutants, verdicts)
    return {one.label.strip(): one for one in found}


def test_a_label_is_scored_against_the_cause_its_mode_implies():
    """`syntax` expects `slip`; `gap` and `rust` expect `form`."""
    labels = [label(f"a{n}", FailureMode.SYNTAX) for n in range(MINIMUM)]
    labels += [label(f"b{n}", FailureMode.GAP) for n in range(MINIMUM)]
    diagnoses = [diagnosis(f"a{n}", Cause.SLIP if n < 7 else Cause.FORM) for n in range(MINIMUM)]
    diagnoses += [diagnosis(f"b{n}", Cause.FORM) for n in range(MINIMUM)]

    found = rows(AT, labels, diagnoses)

    assert found["syntax"].share == 0.7
    assert found["gap"].share == 1.0
    assert found["rust"].read == 0


def test_a_share_over_fewer_than_the_minimum_is_withheld():
    """One label would read as 0% or 100%."""
    found = rows(AT, [label("a", FailureMode.SYNTAX)], [diagnosis("a", Cause.SLIP)])

    assert (found["syntax"].read, found["syntax"].share) == (1, None)


def test_only_the_configuration_scored_is_read():
    """Each configuration is a column, and another's verdicts are not its
    own."""
    found = rows(OTHER, [label("a", FailureMode.GAP)], [diagnosis("a", Cause.FORM)])

    assert found["gap"].read == 0


def test_a_verdict_counts_only_under_the_tool_set_it_was_given():
    """A tool's column beside the baseline's is the difference the tool made,
    so neither column reads the other's verdicts."""
    tooled = replace(TASKS, tools=frozenset({Tool.DIVERGENCE}))
    one = mutant(1, Operator.BOUNDARY)
    baseline = [verdict(one, Cause.FORM)]

    assert rows(AT, [], [], [one], baseline)["mutants"].read == 1
    assert rows(AT, [], [], [one], baseline, tasks=tooled)["mutants"].read == 0
    assert (
        rows(AT, [], [], [one], [verdict(one, Cause.FORM, tooled)], tasks=tooled)["mutants"].read
        == 1
    )


def test_the_mutants_are_a_row_apart_and_split_by_operator():
    """A call strong on templates and weak on attempts has to show as such."""
    mutants = [mutant(n, Operator.CONSTANT) for n in range(4)] + [mutant(9, Operator.BOUNDARY)]
    verdicts = [verdict(one, Cause.FORM) for one in mutants[:3]] + [verdict(mutants[4], Cause.SLIP)]

    found = rows(AT, [], [], mutants, verdicts)

    assert (found["mutants"].read, found["mutants"].matched) == (4, 3)
    assert (found["constant"].read, found["constant"].matched) == (3, 3)
    assert (found["boundary"].read, found["boundary"].matched) == (1, 0)
    assert found["syntax"].read == 0


def test_the_form_code_column_reads_no_mutant():
    """A verdict written beside the clean form would score a leaked answer."""
    tooled = replace(TASKS, tools=frozenset({Tool.FORM_CODE}))
    one = mutant(1, Operator.BOUNDARY)

    found = rows(AT, [], [], [one], [verdict(one, Cause.FORM, tooled)], tasks=tooled)

    assert found["mutants"].read == 0


def test_a_printed_share_carries_its_interval():
    """7 of 10 prints as the shared scorer prints every share."""
    labels = [label(f"a{n}", FailureMode.SYNTAX) for n in range(MINIMUM)]
    diagnoses = [diagnosis(f"a{n}", Cause.SLIP if n < 7 else Cause.FORM) for n in range(MINIMUM)]

    assert cell(rows(AT, labels, diagnoses)["syntax"]) == "70% [40–89%] of 10"
