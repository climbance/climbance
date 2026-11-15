import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from climb.knowledge.schedule import FSRS, history, passed, replay, servable, state
from climb.schema.knowledge import Answer, OpenGrade

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "knowledge" / "scheduling.json").read_text()
)
# the fixture predates the glossary's name for the state
STATE_NAMES = {"mastered": "retained"}


def answer(n: int, line: dict[str, Any]) -> Answer:
    at = datetime.fromisoformat(line["t"])
    return Answer(
        id=f"a-{n}",
        client_id=f"c-{n}",
        user_id="u-4f9c2a",
        device="d-1",
        at=at,
        created_at=at,
        question_id=f"{line['course']}:{line['id']}",
        correct=line["ok"],
        guess=line.get("guess", False),
        grade=OpenGrade(line["grade"]) if "grade" in line else None,
    )


def test_the_published_settings_are_the_fixtures():
    """The server replays with the settings every client was checked against."""
    assert FIXTURE["gating"][0]["snapshot"]["rules"]["fsrs"] == FSRS


@pytest.mark.parametrize("case", FIXTURE["scheduling"], ids=lambda c: c["name"])
def test_replay_matches_the_shared_fixture(case: dict[str, Any]):
    """Python replays each case to the state and due time TypeScript does."""
    answers = [answer(n, line) for n, line in enumerate(case["records"])]
    reviews = next(iter(history(answers).values()), [])
    nows = [datetime.fromisoformat(n) for n in case["now"]]
    want = case["expected"]

    assert [int(r.rating) for r in reviews] == want["ratings"]
    assert passed(reviews) is want["passed"]
    assert [state(reviews, n) for n in nows] == [STATE_NAMES.get(s, s) for s in want["status"]]
    assert [servable(reviews, n) for n in nows] == want["ready"]
    memory = replay(reviews)
    if want["due"] is None:
        assert memory is None
        return
    assert memory is not None
    assert memory.stability == pytest.approx(want["stability"], rel=1e-6)
    assert memory.difficulty == pytest.approx(want["difficulty"], rel=1e-6)
    assert abs((memory.due - datetime.fromisoformat(want["due"])).total_seconds()) <= 60
