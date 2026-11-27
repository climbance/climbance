import concurrent.futures as cf
from pathlib import Path

from helpers import browsing
from test_seed_knowledge import authored

from climb.knowledge import read_module, seed_module
from climb.knowledge.authoring.course import Report, load
from climb.knowledge.authoring.execution import Runs
from climb.knowledge.authoring.tracing import traced
from climb.knowledge.check import refusals

USER = "u-4f9c2a"

ENVIRONMENT = """\
TOOLS = ("find", "refund")


class Environment:
    def __init__(self):
        self.refunded = []

    def find(self, customer):
        return {"ana": [41, 42], "ben": [43]}.get(customer, [])

    def refund(self, number):
        self.refunded.append(number)
        return f"refunded {number}"

    def goal(self, answer):
        return self.refunded == [42] and answer is not None

    def state(self):
        return f"refunded: {self.refunded}"
"""

TRACE = """\
[[drill]]
id = "trc-other-order"
format = "trace"
kind = "concept"
level = 0
prompt = "Ana asked for a refund of order 42. Tap the first wrong step."
lesson = "names#binding"
environment = "shop"
k = 2
end_state = "refunded: [41]"
corrected_end_state = "refunded: [42]"
explain = "Order 41 is not the order Ana named."

[[drill.step]]
call = "find"
args = { customer = "ana" }
result = [41, 42]

[[drill.step]]
call = "refund"
args = { number = 41 }
result = "refunded 41"

[[drill.step]]
say = "Refunded order 41."

[[drill.corrected]]
call = "refund"
args = { number = 42 }
result = "refunded 42"

[[drill.corrected]]
say = "Refunded order 42."
"""


def with_trace(tmp_path: Path, text: str = TRACE) -> Path:
    base = authored(tmp_path)
    (base / "drills" / "core").mkdir(parents=True)
    (base / "drills" / "core" / "flow.toml").write_text(text)
    (base / "environments").mkdir()
    (base / "environments" / "shop.py").write_text(ENVIRONMENT)
    return base


def checked(base: Path) -> Report:
    report = Report()
    with cf.ThreadPoolExecutor(2) as pool:
        traced(load(base), report, pool, Runs())
    return report


def items(base: Path) -> list[dict]:
    source = read_module(base)
    return [q for bank in source.banks for q in bank.questions if q.get("format") == "trace"]


def test_a_trace_reads_with_its_calls_rendered(tmp_path):
    """A client runs no Python, so the reader renders each call and result."""
    (item,) = items(with_trace(tmp_path))

    assert item["steps"] == [
        {"call": "find(customer='ana')", "result": "[41, 42]"},
        {"call": "refund(number=41)", "result": "refunded 41"},
        {"say": "Refunded order 41."},
    ]
    assert item["corrected"][0] == {"call": "refund(number=42)", "result": "refunded 42"}
    assert refusals(read_module(with_trace(tmp_path / "again"))) == []


def test_a_corrected_run_repeating_the_key_step_is_refused(tmp_path):
    """The key is the first step the runs differ at, so they differ there."""
    repeating = TRACE.replace("number = 42", "number = 41").replace(
        'result = "refunded 42"', 'result = "refunded 41"'
    )

    found = refusals(read_module(with_trace(tmp_path, repeating)))

    assert any("the corrected run repeats step 2" in line for line in found)


def test_a_key_step_past_the_run_is_refused(tmp_path):
    found = refusals(read_module(with_trace(tmp_path, TRACE.replace("k = 2", "k = 9"))))

    assert any("k 9 is past the 3 steps" in line for line in found)


def test_a_call_wider_than_a_phone_taps_is_refused(tmp_path):
    wide = TRACE.replace('customer = "ana"', f'customer = "{"a" * 60}"', 1)

    found = refusals(read_module(with_trace(tmp_path, wide)))

    assert any("step 1 holds a line wider than 60 characters" in line for line in found)


def test_the_replay_proves_the_key(tmp_path):
    """Rule 35: the failed run misses the goal, the corrected run reaches it."""
    assert checked(with_trace(tmp_path)).errors == []


def test_a_failed_run_reaching_the_goal_is_refused(tmp_path):
    passing = (
        TRACE.replace("number = 41", "number = 42")
        .replace('"refunded 41"', '"refunded 42"')
        .replace('end_state = "refunded: [41]"', 'end_state = "refunded: [42]"')
    )

    errors = checked(with_trace(tmp_path, passing)).errors

    assert any("the failed run: reaches the goal" in line for line in errors)


def test_a_stored_result_the_environment_does_not_give_is_refused(tmp_path):
    typed = TRACE.replace("result = [41, 42]", "result = [41]")

    errors = checked(with_trace(tmp_path, typed)).errors

    assert any("call 1 returns [41, 42], where the item stores [41]" in line for line in errors)


def test_a_missing_environment_is_refused(tmp_path):
    errors = checked(with_trace(tmp_path, TRACE.replace('"shop"', '"bank"'))).errors

    assert any("no environment environments/bank.py" in line for line in errors)


def test_a_trace_drill_reaches_the_app_with_the_drills(database, tmp_path):
    seed_module(read_module(with_trace(tmp_path)), root=database)

    (course,) = browsing(database, USER).get("/api/knowledge/snapshot").json()["courses"]

    assert not any(q.get("format") == "trace" for q in course["questions"])
    assert [(d["id"], d["k"]) for d in course["drills"]] == [("trc-other-order", 2)]
