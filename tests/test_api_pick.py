from helpers import browsing
from test_api_reads import a_card

from climb.cards import CardStore
from climb.log import PredictionLog
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


def test_taking_the_pick_stores_its_prediction_once(database):
    """A second take before any outcome returns the first prediction."""
    CardStore(database).put(a_card("basic", "binary-search"))
    client = browsing(database, USER)

    first = client.post("/api/pick", json={"card_slug": "basic"}).json()
    again = client.post("/api/pick", json={"card_slug": "basic"}).json()

    assert first["id"] == again["id"]
    assert (first["act"], first["rank"], first["execution"]) == ("start", 5, None)
    assert first["fsrs_settings"] and first["execution_settings"]
    assert len(PredictionLog(database).for_user(USER)) == 1


def test_a_pick_the_board_no_longer_shows_is_refused(database):
    """A prediction about an act the schedule did not choose would mislead."""
    CardStore(database).put(a_card("basic", "binary-search"))

    taken = browsing(database, USER).post("/api/pick", json={"card_slug": "other"})

    assert taken.status_code == 409
    assert PredictionLog(database).for_user(USER) == []
