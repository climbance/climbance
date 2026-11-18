import json

from helpers import T0, FakeTransport, Verdict, make_problem
from matching import card, seeded, template

from climb.calls import CallLog
from climb.diagnoser import DEFAULT
from climb.diagnosing import Tasks, diagnose_attempts, diagnose_mutants, sample
from climb.judging.labelled import LabelledMutant
from climb.log import AttemptLog
from climb.mutant_diagnoses import MutantDiagnosisLog
from climb.mutation import Operator
from climb.problems import ProblemStore
from climb.schema import Attempt, CaseOutcome, Cause, FailureMode

FORM = json.dumps({"cause": "form", "evidence": "the bound moves the wrong way"})


def replying(count: int = 4) -> FakeTransport:
    return FakeTransport.answering(*(Verdict(text=FORM) for _ in range(count)))


def setup(database, *, solved: bool = False):
    cards = seeded(database, card(templates=[template("largest")]))
    form = cards[0].templates[0]
    problem = make_problem("p1", target_technique=None, target_template_id=form.id)
    ProblemStore(database).put(problem)
    log = AttemptLog(database)
    log.append_attempt(
        Attempt(
            id="a1", user_id="u-4f9c2a", problem_id="p1", finished_at=T0, solved=solved, code="x"
        )
    )
    return log, Tasks(problems={problem.id: problem}, templates={form.id: form})


def test_a_failed_attempt_gets_a_diagnosis_carrying_its_call(database):
    log, tasks = setup(database)
    client = replying()

    result = diagnose_attempts(client, log, CallLog(database), tasks)

    (one,) = log.diagnoses()
    assert result.diagnosed == 1
    assert (one.attempt_id, one.cause, one.model) == ("a1", Cause.FORM, DEFAULT.model)
    assert one.call_id is not None


def test_the_call_is_told_the_form_by_name_and_never_shown_its_code(database):
    """Beside a mutant, the clean form's code is the answer: `log.md`."""
    log, tasks = setup(database)
    client = replying()

    diagnose_attempts(client, log, CallLog(database), tasks)

    (form,) = tasks.templates.values()
    sent = client.calls[0]["content"]
    assert f"{form.title}: {form.trigger}" in sent
    assert form.code not in sent


def test_a_solved_attempt_is_not_diagnosed(database):
    log, tasks = setup(database, solved=True)

    result = diagnose_attempts(replying(), log, CallLog(database), tasks)

    assert result.diagnosed == 0
    assert log.diagnoses() == []


def test_an_attempt_read_at_this_configuration_and_prompt_is_skipped(database):
    """A second run pays only for what the first did not read."""
    log, tasks = setup(database)
    diagnose_attempts(replying(), log, CallLog(database), tasks)

    again = diagnose_attempts(replying(), log, CallLog(database), tasks)

    assert (again.diagnosed, again.skipped) == (0, 1)


def mutant(template_id: str, operator: Operator, line: int = 1) -> LabelledMutant:
    return LabelledMutant(
        template_id=template_id,
        form_digest="d1",
        code=f"def solve():\n    return {line}\n",
        line=line,
        change="< → <=",
        operator=operator,
        mode=FailureMode.RUST,
        case_args=[],
        case_expected=1,
        outcome=CaseOutcome.WRONG,
        returned=2,
    )


def test_a_mutant_verdict_is_a_record_of_its_own_and_read_once(database):
    """A mutant is no attempt, so its verdict keys to the mutant itself."""
    _, tasks = setup(database)
    (template_id,) = tasks.templates
    stored = MutantDiagnosisLog(database)
    mutants = [mutant(template_id, Operator.BOUNDARY)]

    first = diagnose_mutants(replying(), stored, CallLog(database), mutants, tasks)
    again = diagnose_mutants(replying(), stored, CallLog(database), mutants, tasks)

    (one,) = stored.all()
    assert (one.template_id, one.cause) == (template_id, Cause.FORM)
    assert (first.diagnosed, again.diagnosed, again.skipped) == (1, 0, 1)


def test_the_sample_takes_the_first_of_each_operator():
    """The same mutants for every configuration, and no operator crowding out
    the rest."""
    mutants = [mutant("t", Operator.CONSTANT, line) for line in range(1, 5)] + [
        mutant("t", Operator.BOUNDARY, 9)
    ]

    kept = sample(mutants, 2)

    assert [(one.operator, one.line) for one in kept] == [
        (Operator.CONSTANT, 1),
        (Operator.CONSTANT, 2),
        (Operator.BOUNDARY, 9),
    ]
    assert sample(mutants, None) == mutants
