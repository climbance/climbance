import concurrent.futures as cf
from pathlib import Path

from helpers import browsing
from test_seed_knowledge import authored

from climb.knowledge import read_module, seed_module
from climb.knowledge.authoring.course import Report, load
from climb.knowledge.authoring.execution import Runs
from climb.knowledge.authoring.judging import judged
from climb.knowledge.check import refusals
from climb.knowledge.schedule import rating
from climb.schema.knowledge import Answer

USER = "u-4f9c2a"

JUDGE = """\
[[drill]]
id = "jdg-chunks"
format = "judge"
kind = "concept"
level = 0
prompt = "Is this chunker correct, or is one span of lines wrong?"
lesson = "names#binding"
lines = '''
def chunks(words, size, overlap):
    step = size - overlap
    out = []
    for i in range(0, len(words), step):
        out.append(words[i : i + size])
    return out
'''
input = 'chunks("a b c d e".split(), 2, 1)'
check = '''
def check(output):
    return all(output[i][-1] == output[i + 1][0] for i in range(len(output) - 1))
'''
output = "[['a', 'b'], ['b', 'c'], ['c', 'd'], ['d', 'e'], ['e']]"
explain = "Each chunk starts on the last word of the one before."

[[drill.variant]]
id = "no-overlap"
lines = '''
def chunks(words, size, overlap):
    step = size
    out = []
    for i in range(0, len(words), step):
        out.append(words[i : i + size])
    return out
'''
span = [2, 2]
output = "[['a', 'b'], ['c', 'd'], ['e']]"
explain = "The step ignores the overlap, so no word is shared."
"""


def with_judge(tmp_path: Path, text: str = JUDGE) -> Path:
    base = authored(tmp_path)
    (base / "drills" / "core").mkdir(parents=True)
    (base / "drills" / "core" / "flow.toml").write_text(text)
    return base


def checked(base: Path) -> Report:
    report = Report()
    with cf.ThreadPoolExecutor(2) as pool:
        judged(load(base), report, pool, Runs())
    return report


def test_an_artefact_reads_as_its_clean_item_and_one_per_variant(tmp_path):
    source = read_module(with_judge(tmp_path))

    items = [q for bank in source.banks for q in bank.questions if q.get("format") == "judge"]

    assert [(q["id"], q.get("span"), q.get("fix")) for q in items] == [
        ("jdg-chunks", None, None),
        ("jdg-chunks-no-overlap", [2, 2], ["    step = size - overlap"]),
    ]
    assert refusals(source) == []


def test_a_stated_span_the_texts_contradict_is_refused(tmp_path):
    """A tap is scored on the span, so a wrong span marks a right tap wrong."""
    found = refusals(read_module(with_judge(tmp_path, JUDGE.replace("[2, 2]", "[2, 3]"))))

    assert any("span [2, 3], where it is (2, 2)" in line for line in found)


def test_a_variant_that_only_deletes_lines_is_refused(tmp_path):
    deleting = JUDGE.replace("    step = size\n", "")

    found = refusals(read_module(with_judge(tmp_path, deleting)))

    assert any("only deletes lines" in line for line in found)


def test_a_line_wider_than_a_phone_taps_is_refused(tmp_path):
    wide = JUDGE.replace("    out = []\n    for", f"    out = []  # {'x' * 60}\n    for", 1)

    found = refusals(read_module(with_judge(tmp_path, wide)))

    assert any("line 3 is wider than 60 characters" in line for line in found)


def test_the_witness_proves_each_item_s_key(tmp_path):
    """Rule 34: the clean lines pass the check and the variant's fail it."""
    assert checked(with_judge(tmp_path)).errors == []


def test_a_variant_passing_the_check_is_refused(tmp_path):
    passing = JUDGE.replace("    step = size\n", "    step = size - overlap  # same\n")

    errors = checked(with_judge(tmp_path, passing)).errors

    assert any("the variant passes the check" in line for line in errors)


def test_a_stored_output_the_lines_do_not_give_is_refused(tmp_path):
    typed = JUDGE.replace("[['a', 'b'], ['c', 'd'], ['e']]", "[['a', 'b'], ['c', 'd']]")

    (error,) = checked(with_judge(tmp_path, typed)).errors

    assert "variant no-overlap: the lines give [['a', 'b'], ['c', 'd'], ['e']]" in error


def test_a_right_verdict_on_the_wrong_line_rates_hard(tmp_path):
    """Spotting and locating are counted apart: `content-repo/ai-drills.md`."""
    at = {
        "id": "a-1",
        "client_id": "c-1",
        "user_id": USER,
        "device": "d-1",
        "at": "2026-11-27T10:00:00Z",
        "created_at": "2026-11-27T10:00:01Z",
        "question_id": "q-1",
        "correct": True,
        "called_clean": False,
    }

    spotted = Answer.model_validate(at | {"tapped": 4, "located": False})
    located = Answer.model_validate(at | {"tapped": 2, "located": True})

    assert (rating(spotted).name, rating(located).name) == ("Hard", "Good")


def test_a_judge_drill_reaches_the_app_with_the_drills(database, tmp_path):
    seed_module(read_module(with_judge(tmp_path)), root=database)

    (course,) = browsing(database, USER).get("/api/knowledge/snapshot").json()["courses"]

    assert not any(q.get("format") == "judge" for q in course["questions"])
    assert [(d["id"], d.get("span")) for d in course["drills"]] == [
        ("jdg-chunks", None),
        ("jdg-chunks-no-overlap", [2, 2]),
    ]
