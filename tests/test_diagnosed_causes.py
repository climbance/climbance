import pytest
from helpers import PROVENANCE_FIELDS, T0, make_problem

from climb.diagnoser import Tool, request_hash, system_digest
from climb.diagnosing import Tasks, measured_causes
from climb.diagnosing import causes as module
from climb.schema import Attempt, Cause, Configuration, Diagnosis, Template

AT = Configuration(
    model=PROVENANCE_FIELDS["model"],
    effort=PROVENANCE_FIELDS["effort"],
    pin=PROVENANCE_FIELDS["pin"],
    temperature=None,
)
PROBLEMS = {"p1": make_problem("p1", target_technique=None, target_template_id="t1")}
TEMPLATES = {"t1": Template(id="t1", slug="form", title="Form", trigger="t", code="x")}
FAILED = Attempt(
    id="a1", user_id="u-4f9c2a", problem_id="p1", finished_at=T0, solved=False, code="a1"
)


def diagnosis(cause: Cause, tools: frozenset[Tool] = frozenset(), **fields) -> Diagnosis:
    tasks = Tasks(PROBLEMS, TEMPLATES, tools=tools)
    asked = request_hash(tasks.attempt(FAILED), FAILED.code or "")
    return Diagnosis(
        id=f"d-{cause}",
        created_at=T0,
        attempt_id=FAILED.id,
        cause=cause,
        evidence="a line",
        **PROVENANCE_FIELDS | {"prompt_hash": asked} | fields,
    )


def read(*diagnoses: Diagnosis) -> dict[str, Cause]:
    return measured_causes(PROBLEMS, TEMPLATES, [FAILED], list(diagnoses))


@pytest.fixture
def measured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(module, "MEASURED", {AT: system_digest()})


@pytest.mark.usefixtures("measured")
def test_a_measured_configurations_latest_baseline_diagnosis_is_read():
    """The latest verdict of the measured configuration names the cause."""
    assert read(diagnosis(Cause.FORM), diagnosis(Cause.SLIP)) == {"a1": Cause.SLIP}


@pytest.mark.usefixtures("measured")
def test_a_configuration_nobody_measured_is_not_read():
    """Another model's verdict aims nothing, however it reads."""
    assert read(diagnosis(Cause.SLIP, model="another-model")) == {}


@pytest.mark.usefixtures("measured")
def test_a_verdict_given_a_tool_is_not_read():
    """A tool's column is measured apart from the baseline's."""
    assert read(diagnosis(Cause.SLIP, frozenset({Tool.FORM_CODE}))) == {}


def test_a_changed_system_prompt_is_not_read(monkeypatch: pytest.MonkeyPatch):
    """The measurement read another prompt, so nothing is measured."""
    monkeypatch.setattr(module, "MEASURED", {AT: "another-digest"})
    assert read(diagnosis(Cause.SLIP)) == {}
