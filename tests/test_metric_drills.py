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

LIBRARY = """\
def accuracy(outputs, expected):
    return sum(o == e for o, e in zip(outputs, expected)) / len(expected)


def caught(outputs, expected, positive):
    held = [o for o, e in zip(outputs, expected) if e == positive]
    return sum(o == positive for o in held) / len(held)
"""

METRIC = """\
[[drill]]
id = "flow-fraud"
format = "metric"
kind = "concept"
level = 0
prompt = "A missed fraud costs most. Which metric decides?"
lesson = "names#binding"
expected = ["ok", "ok", "ok", "fraud"]
a = ["ok", "ok", "ok", "ok"]
b = ["ok", "fraud", "ok", "fraud"]
candidates = [
  { metric = "accuracy", label = "Accuracy" },
  { metric = "caught", label = "Fraud caught", params = { positive = "fraud" } },
]
utility = '''
def utility(outputs, expected):
    return -sum(o == "ok" and e == "fraud" for o, e in zip(outputs, expected))
'''
scores = [[0.75, 0.75], [0.0, 1.0]]
goal = [-1, 0]
explain = "Accuracy ties the two, and only the fraud caught tells them apart."
"""


def with_metric(tmp_path: Path, text: str = METRIC, library: str | None = LIBRARY) -> Path:
    base = authored(tmp_path)
    (base / "drills" / "core").mkdir(parents=True)
    (base / "drills" / "core" / "flow.toml").write_text(text)
    if library is not None:
        (base / "metrics.py").write_text(library)
    return base


def checked(base: Path) -> Report:
    report = Report()
    with cf.ThreadPoolExecutor(2) as pool:
        drills(load(base), report, pool, Runs())
    return report


def test_a_metric_drill_with_one_agreeing_candidate_is_taken(tmp_path):
    assert refusals(read_module(with_metric(tmp_path))) == []


def test_a_metric_drill_where_two_candidates_agree_is_refused(tmp_path):
    """Two right options would mark a right pick wrong."""
    both = METRIC.replace("[[0.75, 0.75], [0.0, 1.0]]", "[[0.5, 0.75], [0.0, 1.0]]")

    found = refusals(read_module(with_metric(tmp_path, both)))

    assert any("exactly one candidate" in line for line in found)


def test_a_metric_drill_whose_goal_ties_the_systems_is_refused(tmp_path):
    found = refusals(
        read_module(with_metric(tmp_path, METRIC.replace("goal = [-1, 0]", "goal = [0, 0]")))
    )

    assert any("ties the two systems" in line for line in found)


def test_a_metric_drill_s_scores_are_what_the_library_gives(tmp_path):
    """Rule 33: a score typed by hand would decide the key unchecked."""
    assert checked(with_metric(tmp_path)).errors == []

    typed = METRIC.replace("[[0.75, 0.75],", "[[0.8, 0.75],")
    (error,) = checked(with_metric(tmp_path / "typed", typed)).errors

    assert "accuracy scores [0.75, 0.75]" in error


def test_a_metric_drill_s_goal_is_what_its_utility_gives(tmp_path):
    (error,) = checked(
        with_metric(tmp_path, METRIC.replace("goal = [-1, 0]", "goal = [-2, 0]"))
    ).errors

    assert "the goal scores [-1, 0]" in error


def test_a_metric_drill_needs_the_module_s_library(tmp_path):
    (error,) = checked(with_metric(tmp_path, library=None)).errors

    assert "metric library" in error


def test_a_metric_drill_reaches_the_app_with_the_drills(database, tmp_path):
    seed_module(read_module(with_metric(tmp_path)), root=database)

    (course,) = browsing(database, USER).get("/api/knowledge/snapshot").json()["courses"]

    assert "flow-fraud" not in [q["id"] for q in course["questions"]]
    (drill,) = course["drills"]
    assert (drill["format"], drill["goal"], drill["scores"][1]) == ("metric", [-1, 0], [0.0, 1.0])
