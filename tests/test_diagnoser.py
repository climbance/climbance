import json

from helpers import FakeTransport, Verdict

from climb.diagnoser import Task, diagnose, prompt, request_hash
from climb.schema import Cause

CODE = "def solve(xs):\n    return xs[0]\n"
TASK = Task(statement="Return the largest value.", form="largest: the largest value")


class Kept:
    def __init__(self) -> None:
        self.appended = []

    def append(self, record) -> None:
        self.appended.append(record)


def replying(text: str | None, stop_reason: str = "stop") -> FakeTransport:
    return FakeTransport.answering(Verdict(text=text, stop_reason=stop_reason))


def test_the_reading_is_the_cause_and_the_evidence_named():
    client = replying(json.dumps({"cause": "slip", "evidence": "the name is misspelled"}))

    reading, call = diagnose(client, Kept(), TASK, CODE)

    assert reading is not None
    assert (reading.cause, reading.evidence) == (Cause.SLIP, "the name is misspelled")
    assert call.response is not None


def test_a_refusal_and_a_reply_cut_short_name_no_cause():
    """Neither is a verdict, and a record written from one would be scored as
    one."""
    refused, _ = diagnose(replying(None, "content_filter"), Kept(), TASK, CODE)
    cut, _ = diagnose(replying('{"cause": "form"', "length"), Kept(), TASK, CODE)

    assert refused is None
    assert cut is None


def test_the_prompt_carries_the_task_the_form_named_and_the_code():
    sent = prompt(TASK, CODE)

    assert TASK.statement in sent
    assert "largest: the largest value" in sent
    assert CODE in sent


def test_a_problem_written_for_no_template_sends_no_form():
    """A technique target names no form, and an empty tag would read as one."""
    assert "<form>" not in prompt(Task(statement="Return the largest value."), CODE)


def test_the_request_hash_moves_with_the_code():
    """Staleness keys on it, so two codes sharing a hash would share a
    verdict."""
    assert request_hash(TASK, CODE) != request_hash(TASK, CODE + "\n# again\n")
