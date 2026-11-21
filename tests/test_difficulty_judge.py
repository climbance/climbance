from datetime import timedelta

import pytest
from commands import connected, run_cli
from helpers import PROVENANCE_FIELDS, T0, FakeTransport, Verdict, make_problem
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from climb.calls import CallLog
from climb.difficulty import DRAWS, Anchor, correct, draw, rating, standing_correction
from climb.difficulty.judge import INSTRUCTIONS_HASH, current, judged, medians
from climb.problems import ProblemStore
from climb.ratings import CorrectionLog, DrawLog, RatingLog
from climb.schema import DifficultyDraw, RatingSource


def a_draw(problem_id: str, value: int, n: int = 0) -> DifficultyDraw:
    return DifficultyDraw(
        id=f"d-{problem_id}-{n}",
        created_at=T0 + timedelta(seconds=n),
        problem_id=problem_id,
        judged=value,
        **PROVENANCE_FIELDS,
    )


def anchored(line=(100.0, 0.8), count: int = 12) -> tuple[list[DifficultyDraw], dict]:
    """Anchors whose rating lies on `line` from their judged median, every
    third held out and 50 points off it, each drawn `DRAWS` times around that
    median."""
    intercept, slope = line
    anchors, draws = {}, []
    for k in range(count):
        judged_at = 1000 + 100 * k
        held_out = k % 3 == 0
        off = (50 if k % 2 else -50) if held_out else 0
        anchors[f"a{k}"] = Anchor(rating=intercept + slope * judged_at + off, held_out=held_out)
        spread = [judged_at - 20, judged_at + 20] * (DRAWS // 2) + [judged_at] * (DRAWS % 2)
        draws += [a_draw(f"a{k}", v, n) for n, v in enumerate(spread)]
    return draws, anchors


def test_the_rating_is_the_last_number_on_the_last_line():
    assert judged("It needs a segment tree.\nRating: 1900") == 1900
    assert judged("about 1400\n\n1600\n") == 1600


@pytest.mark.parametrize("reply", [None, "", "hard", "Rating: 99", "Rating: 9000", "1500\nhard"])
def test_a_reply_holding_no_rating_reads_as_none(reply):
    """A number off the scale is a misread; only the last line is read."""
    assert judged(reply) is None


def test_the_correction_recovers_the_line_the_anchors_lie_on():
    draws, anchors = anchored()

    correction = correct(draws, anchors, anchor_set="h1")

    assert (round(correction.intercept, 6), round(correction.slope, 6)) == (100.0, 0.8)
    assert (correction.anchors_fitted, correction.anchors_held_out) == (8, 4)
    assert correction.held_out_spearman == pytest.approx(1.0)
    assert correction.held_out_mean_error == pytest.approx(50.0)
    assert correction.instructions_hash == INSTRUCTIONS_HASH
    assert correction.draws == DRAWS


def test_an_anchor_short_of_the_draws_is_left_out_of_the_line():
    """A median of fewer draws is not the judge the correction names."""
    draws, anchors = anchored()
    draws = [d for d in draws if not (d.problem_id == "a1" and d.id.endswith("-0"))]

    correction = correct(draws, anchors, anchor_set="h1")

    assert correction.anchors_fitted == 7


def test_no_correction_without_two_held_out_anchors():
    draws, anchors = anchored(count=3)

    with pytest.raises(ValueError, match="held-out"):
        correct(draws, anchors, anchor_set="h1")


def test_no_correction_where_harder_anchors_are_judged_easier():
    draws, anchors = anchored(line=(3000.0, -0.8))

    with pytest.raises(ValueError, match="easier"):
        correct(draws, anchors, anchor_set="h1")


def test_a_rating_is_the_corrected_median_of_its_draws():
    draws, anchors = anchored()
    correction = correct(draws, anchors, anchor_set="h1")
    mine = [a_draw("p1", v, n) for n, v in enumerate([1500, 1400, 1600, 1500, 2600, 1450])]

    made = rating("p1", mine, correction)

    assert made.score == pytest.approx(100 + 0.8 * 1500)
    assert made.deviation == correction.deviation
    assert (made.source, made.correction_id) == (RatingSource.JUDGE, correction.id)
    assert made.draw_ids == [one.id for one in mine]


def test_medians_read_the_first_draws_of_each_problem():
    draws = [a_draw("p1", 1000 + n, n) for n in range(DRAWS + 2)] + [a_draw("p2", 1000)]

    read = medians(draws, DRAWS)

    assert list(read) == ["p1"]
    assert [one.judged for one in read["p1"]] == [1000 + n for n in range(DRAWS)]


def test_the_latest_correction_matching_the_judge_stands():
    draws, anchors = anchored()
    first = correct(draws, anchors, anchor_set="h1")
    later = first.model_copy(update={"id": "c2", "created_at": first.created_at + timedelta(1)})
    other = later.model_copy(
        update={"id": "c3", "created_at": later.created_at + timedelta(1), "instructions_hash": "x"}
    )

    assert standing_correction([first, later, other]) == later
    assert standing_correction([other]) is None


def test_a_draw_carries_its_calls_provenance_and_the_current_prompt(database):
    calls = CallLog(database)

    _, made = draw("p1", "a statement", transport=answering("1700"), calls=calls)
    _, unread = draw("p1", "a statement", transport=answering("no idea"), calls=calls)

    assert made is not None and made.judged == 1700
    assert current(made, "a statement")
    assert not current(made, "another statement")
    assert unread is None
    assert len(calls.all()) == 3  # the database fixture's call, and the two


def test_a_judge_rating_reads_back_with_its_draws_and_is_never_rewritten(database):
    """Product data, append-only; the links are written with the rating."""
    ProblemStore(database).put(make_problem())
    draws, anchors = anchored()
    correction = correct(draws, anchors, anchor_set="h1")
    CorrectionLog(database).append(correction)
    mine = [a_draw("p1", 1500, n) for n in range(DRAWS)]
    for one in mine:
        DrawLog(database).append(one)
    made = rating("p1", mine, correction)
    RatingLog(database).append(made)

    assert RatingLog(database).for_problem("p1") == [made]
    assert CorrectionLog(database).all() == [correction]
    for table in ("difficulty_draws", "difficulty_rating_draws", "difficulty_corrections"):
        with pytest.raises(DBAPIError), database.begin() as conn:
            conn.execute(text(f"DELETE FROM {table}"))


def test_the_judge_run_rates_each_served_problem_once(database, monkeypatch):
    """Stored draws are read again, so a second run makes no call."""
    connected(database, monkeypatch)
    ProblemStore(database).put(make_problem())
    draws, anchors = anchored()
    CorrectionLog(database).append(correct(draws, anchors, anchor_set="h1"))
    client = FakeTransport.answering(*[Verdict(text="1500")] * DRAWS)

    run_cli(monkeypatch, "difficulty", "judge", "--write", client=client)
    run_cli(monkeypatch, "difficulty", "judge", "--write", client=client)

    (made,) = RatingLog(database).for_problem("p1")
    assert made.score == pytest.approx(100 + 0.8 * 1500)
    assert len(DrawLog(database).all()) == DRAWS
    assert len(client.calls) == DRAWS


def test_the_judge_run_stores_nothing_without_write(database, monkeypatch):
    connected(database, monkeypatch)
    ProblemStore(database).put(make_problem())
    draws, anchors = anchored()
    CorrectionLog(database).append(correct(draws, anchors, anchor_set="h1"))

    run_cli(
        monkeypatch,
        "difficulty",
        "judge",
        client=FakeTransport.answering(*[Verdict(text="1500")] * DRAWS),
    )

    assert (RatingLog(database).all(), DrawLog(database).all()) == ([], [])


def test_the_judge_run_rates_no_more_than_its_limit(database, monkeypatch):
    connected(database, monkeypatch)
    for id in ("p1", "p2"):
        ProblemStore(database).put(make_problem(id))
    draws, anchors = anchored()
    CorrectionLog(database).append(correct(draws, anchors, anchor_set="h1"))
    client = FakeTransport.answering(*[Verdict(text="1500")] * DRAWS)

    run_cli(monkeypatch, "difficulty", "judge", "--limit", "1", "--write", client=client)

    assert len(RatingLog(database).all()) == 1


def test_the_judge_run_refuses_to_start_with_no_matching_correction(database, monkeypatch):
    connected(database, monkeypatch)

    with pytest.raises(SystemExit):
        run_cli(monkeypatch, "difficulty", "judge", client=FakeTransport.answering())


def test_correct_stores_the_correction_fitted_on_the_anchor_file(database, monkeypatch, tmp_path):
    connected(database, monkeypatch)
    draws, anchors = anchored()
    listed = tmp_path / "anchors.csv"
    listed.write_text(
        "id,rating,split\n"
        + "".join(
            f"{k},{a.rating},{'held_out' if a.held_out else 'fit'}\n" for k, a in anchors.items()
        )
    )
    drawn = tmp_path / "draws.jsonl"
    drawn.write_text("".join(one.model_dump_json() + "\n" for one in draws))

    run_cli(
        monkeypatch, "difficulty", "correct", "--anchors", str(listed), "--anchor-draws", str(drawn)
    )
    assert CorrectionLog(database).all() == []
    run_cli(
        monkeypatch,
        "difficulty",
        "correct",
        "--anchors",
        str(listed),
        "--anchor-draws",
        str(drawn),
        "--write",
    )

    (stored,) = CorrectionLog(database).all()
    assert stored.slope == pytest.approx(0.8)


def answering(reply: str) -> FakeTransport:
    return FakeTransport.answering(Verdict(text=reply))
