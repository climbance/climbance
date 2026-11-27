import concurrent.futures as cf
from pathlib import Path

from helpers import browsing
from test_seed_knowledge import authored

from climb.knowledge import read_module, seed_module
from climb.knowledge.authoring.course import Report, load
from climb.knowledge.authoring.drills import drills
from climb.knowledge.authoring.execution import Runs
from climb.knowledge.check import refusals

USER = "u-4f9c2a"
T = "2026-11-09T10:00:00+00:00"

ESTIMATE = """\
[[drill]]
id = "flow-cost"
format = "estimate"
kind = "concept"
level = 0
prompt = "Estimate the cost of a thousand such calls, in US dollars."
lesson = "names#binding"
received = "A short answer."
given = [
  { name = "calls", label = "Calls", value = 1000 },
  { name = "per_call", label = "Cost of one call, $", value = 0.002 },
]
compute = '''
print(f"{calls} calls at ${per_call} each")
print(calls * per_call)
'''
working = ["1000 calls at $0.002 each"]
computed = 2.0
factor = 2
unit = "US dollars"
explain = "The cost is the calls times the cost of one."
"""


def with_drills(tmp_path: Path, text: str = ESTIMATE) -> Path:
    base = authored(tmp_path)
    (base / "drills" / "core").mkdir(parents=True)
    (base / "drills" / "core" / "flow.toml").write_text(text)
    return base


def checked(base: Path) -> Report:
    report = Report()
    with cf.ThreadPoolExecutor(2) as pool:
        drills(load(base), report, pool, Runs())
    return report


def test_a_drill_is_read_after_its_subtopic_s_questions(tmp_path):
    source = read_module(with_drills(tmp_path))

    (flow,) = [bank for bank in source.banks if bank.sub == "flow"]
    assert [raw["id"] for raw in flow.questions] == ["flow-1", "flow-cost"]
    assert refusals(source) == []


def test_an_estimate_without_its_compute_is_refused(tmp_path):
    source = read_module(with_drills(tmp_path, ESTIMATE.replace("compute =", "program =")))

    assert any("flow-cost" in line and "compute" in line for line in refusals(source))


def test_an_estimate_s_key_is_what_its_compute_prints(tmp_path):
    """Rule 32: a key typed by hand would be served as the engine's."""
    assert checked(with_drills(tmp_path)).errors == []

    wrong = checked(
        with_drills(tmp_path / "wrong", ESTIMATE.replace("computed = 2.0", "computed = 3.0"))
    )

    (error,) = wrong.errors
    assert "the key 2.0" in error


def test_an_estimate_s_working_is_what_its_compute_prints(tmp_path):
    report = checked(with_drills(tmp_path, ESTIMATE.replace("1000 calls at", "1000 calls for")))

    (error,) = report.errors
    assert "working" in error


def test_a_drill_reaches_the_app_apart_from_the_questions(database, tmp_path):
    """An installed app reads `questions` whole, and cannot draw an estimate."""
    seed_module(read_module(with_drills(tmp_path)), root=database)

    (course,) = browsing(database, USER).get("/api/knowledge/snapshot").json()["courses"]

    assert "flow-cost" not in [q["id"] for q in course["questions"]]
    (drill,) = course["drills"]
    assert (drill["id"], drill["format"], drill["computed"], drill["sub"]) == (
        "flow-cost",
        "estimate",
        2.0,
        "flow",
    )


def test_a_module_with_no_drill_carries_no_drills_key(database, tmp_path):
    seed_module(read_module(authored(tmp_path)), root=database)

    (course,) = browsing(database, USER).get("/api/knowledge/snapshot").json()["courses"]

    assert "drills" not in course


def test_an_estimate_answer_round_trips_with_its_number(database, tmp_path):
    """The number is stored, since the factor is still to be set from it."""
    seed_module(read_module(with_drills(tmp_path)), root=database)
    line = {"kind": "attempt", "client_id": "c1", "t": T, "course": "python", "id": "flow-cost",
            "ok": True, "estimate": 3.5}  # fmt: skip
    body = {"device": "phone", "records": [line], "since": {}}

    response = browsing(database, USER).post("/api/knowledge/sync", json=body).json()

    (back,) = response["records"]
    assert back["estimate"] == 3.5
