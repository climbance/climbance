from helpers import browsing
from test_api_reads import a_card

from climb.cards import CardStore
from climb.schema import Requirement

USER = "u-4f9c2a"


def test_no_card_gives_no_pick(database):
    """With nothing to study, the board keeps its lists and serves no pick."""
    assert browsing(database, USER).get("/api/pick").json() is None


def test_the_pick_starts_the_shallowest_unlocked_card(database):
    """With nothing in flight, the pick offers a new card, a root first."""
    root = a_card("basic", "binary-search")
    above = a_card("on-answer", "binary-search").model_copy(
        update={"requires": [Requirement(card="basic", template="core", used_by="core")]}
    )
    CardStore(database).put_all([root, above])

    picked = browsing(database, USER).get("/api/pick").json()

    assert (picked["rank"], picked["act"], picked["card_slug"]) == (5, "start", "basic")
    assert picked["card_title"] == "basic" and picked["problem_id"] is None
