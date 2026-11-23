from dataclasses import replace

from helpers import PROVENANCE_FIELDS, T0, make_problem

from climb.cli.diagnose import cell, score_sets
from climb.diagnoser import Tool, request_hash
from climb.diagnosing import MINIMUM, Tasks, scored, unscored
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
from climb.scorer.spot import SAMPLE, SEED, sheet
from climb.scorer.spot import verdicts as spot_verdicts

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


def mutant(line: int, operator: Operator, mode: FailureMode = FailureMode.RUST) -> LabelledMutant:
    return LabelledMutant(
        template_id="t1",
        form_digest="d1",
        code=f"return {line}\n",
        line=line,
        change="< → <=",
        operator=operator,
        mode=mode,
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
    named, section = {}, ""
    for one in found:
        if one.label.startswith(" "):
            named[f"{section}/{one.label.strip()}"] = one
        else:
            section = one.label
            named[section] = one
    return named


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

    assert rows(AT, [], [], [one], baseline)["form mutants"].read == 1
    assert rows(AT, [], [], [one], baseline, tasks=tooled)["form mutants"].read == 0
    assert (
        rows(AT, [], [], [one], [verdict(one, Cause.FORM, tooled)], tasks=tooled)[
            "form mutants"
        ].read
        == 1
    )


def test_the_mutants_are_a_row_apart_and_split_by_operator():
    """A call strong on templates and weak on attempts has to show as such."""
    mutants = [mutant(n, Operator.CONSTANT) for n in range(4)] + [mutant(9, Operator.BOUNDARY)]
    verdicts = [verdict(one, Cause.FORM) for one in mutants[:3]] + [verdict(mutants[4], Cause.SLIP)]

    found = rows(AT, [], [], mutants, verdicts)

    assert (found["form mutants"].read, found["form mutants"].matched) == (4, 3)
    assert (found["form mutants/constant"].read, found["form mutants/constant"].matched) == (3, 3)
    assert (found["form mutants/boundary"].read, found["form mutants/boundary"].matched) == (1, 0)
    assert found["syntax"].read == 0


def test_the_slip_mutants_are_a_row_apart_implying_slip():
    """The form mutants imply `form` alone, so a call always naming it would
    score well on them."""
    form = mutant(1, Operator.CONSTANT)
    slip = mutant(2, Operator.CONSTANT, FailureMode.SYNTAX)

    found = rows(AT, [], [], [form, slip], [verdict(form, Cause.FORM), verdict(slip, Cause.FORM)])

    assert (found["form mutants"].read, found["form mutants"].matched) == (1, 1)
    assert found["slip mutants"].implied is Cause.SLIP
    assert (found["slip mutants"].read, found["slip mutants"].matched) == (1, 0)
    assert found["slip mutants/constant"].read == 1


def test_the_form_code_column_reads_no_mutant():
    """A verdict written beside the clean form would score a leaked answer."""
    tooled = replace(TASKS, tools=frozenset({Tool.FORM_CODE}))
    one = mutant(1, Operator.BOUNDARY)

    found = rows(AT, [], [], [one], [verdict(one, Cause.FORM, tooled)], tasks=tooled)

    assert found["form mutants"].read == 0


def test_a_printed_share_carries_its_interval():
    """7 of 10 prints as the shared scorer prints every share."""
    labels = [label(f"a{n}", FailureMode.SYNTAX) for n in range(MINIMUM)]
    diagnoses = [diagnosis(f"a{n}", Cause.SLIP if n < 7 else Cause.FORM) for n in range(MINIMUM)]

    assert cell(rows(AT, labels, diagnoses)["syntax"]) == "70% [40–89%] of 10"


def test_a_tool_column_prints_its_gain_over_the_baseline():
    """8 of 10 beside the baseline's 7 of 10 gains 10 points."""
    labels = [label(f"a{n}", FailureMode.SYNTAX) for n in range(MINIMUM)]
    base = [diagnosis(f"a{n}", Cause.SLIP if n < 7 else Cause.FORM) for n in range(MINIMUM)]
    tool = [diagnosis(f"a{n}", Cause.SLIP if n < 8 else Cause.FORM) for n in range(MINIMUM)]
    baseline = rows(AT, labels, base)["syntax"]

    assert cell(rows(AT, labels, tool)["syntax"], baseline) == "80% [49–94%] of 10, +10"
    assert cell(baseline, baseline) == "70% [40–89%] of 10"


def test_no_gain_is_printed_beside_a_withheld_baseline():
    """A baseline under the minimum has no share to subtract."""
    labels = [label(f"a{n}", FailureMode.SYNTAX) for n in range(MINIMUM)]
    tool = [diagnosis(f"a{n}", Cause.SLIP) for n in range(MINIMUM)]
    baseline = rows(AT, labels[:1], tool[:1])["syntax"]

    assert cell(rows(AT, labels, tool)["syntax"], baseline) == "100% [72–100%] of 10"


def test_the_score_stacks_every_tool_after_each_alone():
    """Two tools give four columns: none, each alone, both."""
    both = frozenset(Tool)

    assert score_sets(both) == [
        frozenset(),
        frozenset({Tool.DIVERGENCE}),
        frozenset({Tool.FORM_CODE}),
        both,
    ]
    assert score_sets(frozenset({Tool.DIVERGENCE})) == [frozenset(), frozenset({Tool.DIVERGENCE})]


def test_the_spot_check_reads_the_verdicts_no_self_label_scores():
    """A `gap` label scores its attempt; a `speed` label implies no cause."""
    attempts = [attempt(one) for one in ("a", "b", "c")]
    labels = [label("b", FailureMode.GAP), label("c", FailureMode.SPEED)]
    diagnoses = [diagnosis(one, Cause.FORM) for one in ("a", "b", "c")]

    found = unscored(AT, TASKS, attempts, labels, diagnoses)

    assert [(one.id, one.kind) for one in found] == [("a", "form"), ("c", "form")]
    assert found[0].text == f"{TASKS.problems['p1'].statement}\n\n```python\na\n```"


def test_the_spot_check_reads_one_configurations_latest_verdict():
    """An earlier verdict and another configuration's never reach the sheet."""
    earlier = diagnosis("a", Cause.SLIP)
    other = diagnosis("a", Cause.SLIP).model_copy(update={"model": OTHER.model})
    later = diagnosis("a", Cause.FORM)

    found = unscored(AT, TASKS, [attempt("a")], [], [earlier, later, other])

    assert [(one.id, one.kind) for one in found] == [("a", "form")]


def test_the_exported_verdicts_draw_a_sheet():
    """`diagnose verdicts` prints the lines `spot draw` reads."""
    lines = [
        one.model_dump_json()
        for one in unscored(AT, TASKS, [attempt("a")], [], [diagnosis("a", Cause.SLIP)])
    ]

    drawn = sheet(spot_verdicts(lines), SAMPLE, SEED)

    assert "## slip: 1 of 1" in drawn
    assert "`a`" in drawn
