import json
from typing import Any

import pytest
from scheduling_fixture import FIXTURE, scheduling

from climb.knowledge.schedule import FSRS

STORED = json.loads(FIXTURE.read_text())


def test_the_published_settings_are_the_fixtures():
    """The server replays with the settings every client was checked against."""
    assert STORED["gating"][0]["snapshot"]["rules"]["fsrs"] == FSRS


@pytest.mark.parametrize(
    ("stored", "generated"),
    list(zip(STORED["scheduling"], scheduling(), strict=True)),
    ids=lambda c: c["name"],
)
def test_the_fixture_is_what_the_replay_generates(
    stored: dict[str, Any], generated: dict[str, Any]
):
    """A rule changed without `just fixtures`, or a hand edit, fails."""
    assert stored == generated
