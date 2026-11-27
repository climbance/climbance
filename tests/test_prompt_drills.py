import concurrent.futures as cf
import tomllib
from pathlib import Path

from commands import connected, run_cli
from helpers import FakeTransport, Verdict
from test_seed_knowledge import authored

from climb.calls import CallLog
from climb.knowledge import read_module
from climb.knowledge.authoring.course import Report, load
from climb.knowledge.authoring.execution import Runs
from climb.knowledge.authoring.sampling import sampled
from climb.knowledge.check import refusals

PANEL = '[models]\npanel = ["a/one@p1"]\nevery_days = 90\n'

PROMPT = """\
[[drill]]
id = "jdg-label"
format = "judge"
kind = "concept"
level = 0
prompt = "Is this prompt correct, or is one span of lines wrong?"
lesson = "names#binding"
lines = '''
Label the ticket: billing, bug or other.
Answer with the label alone.

Ticket: {input}
'''
input = "Can I buy a gift card?"
check = '''
def check(output):
    return output.strip().lower() == "other"
'''
share = 0.5
samples = 2
explain = "The set ends in other."

[[drill.variant]]
id = "no-other"
lines = '''
Label the ticket: billing or bug.
Answer with the label alone.

Ticket: {input}
'''
span = [1, 1]
share = 0.5
explain = "No label fits the ticket."
"""

SAMPLES = """\
[[sample]]
side = "clean"
model = "a/one@p1"
call = "c-1"
text = "other"
passed = true

[[sample]]
side = "no-other"
model = "a/one@p1"
call = "c-2"
text = "billing"
passed = false

[[sample]]
side = "no-other"
model = "a/one@p1"
call = "c-3"
text = "other"
passed = true
"""


def with_prompt(tmp_path: Path, samples: str | None = SAMPLES) -> Path:
    base = authored(tmp_path)
    (base / "check.toml").write_text(PANEL)
    (base / "drills" / "core").mkdir(parents=True)
    (base / "drills" / "core" / "flow.toml").write_text(PROMPT)
    if samples is not None:
        (base / "samples").mkdir()
        (base / "samples" / "jdg-label.toml").write_text(samples)
    return base


def checked(base: Path) -> Report:
    report = Report()
    with cf.ThreadPoolExecutor(2) as pool:
        sampled(load(base), report, pool, Runs())
    return report


def test_a_prompt_serves_its_first_answers_and_the_counts(tmp_path):
    """A client runs no model, so the item shows a stored answer as output."""
    source = read_module(with_prompt(tmp_path))

    items = [q for bank in source.banks for q in bank.questions if q.get("format") == "judge"]

    assert [(q["id"], q["output"], q.get("clean_output")) for q in items] == [
        ("jdg-label", "other", None),
        ("jdg-label-no-other", "billing", "other"),
    ]
    assert items[1]["measured"] == [
        "a/one@p1: 1 of 2 answers failed the check, and 1 of 1 to the correct lines passed"
    ]
    assert refusals(source) == []


def test_a_prompt_with_no_samples_is_refused(tmp_path):
    base = with_prompt(tmp_path, samples=None)

    assert any("no samples" in line for line in refusals(read_module(base)))
    assert any("no samples" in line for line in checked(base).errors)


def test_stored_answers_meeting_each_share_prove_the_key(tmp_path):
    """Rule 36: the clean answers pass and each variant's fail, at the share."""
    assert checked(with_prompt(tmp_path)).errors == []


def test_a_side_under_its_share_is_refused(tmp_path):
    under = SAMPLES.replace('text = "billing"\npassed = false', 'text = "other"\npassed = true')

    errors = checked(with_prompt(tmp_path, under)).errors

    assert any("under its share on a/one@p1: no-other 0 of 2" in line for line in errors)


def test_a_stored_verdict_the_check_contradicts_is_refused(tmp_path):
    lying = SAMPLES.replace('text = "billing"\npassed = false', 'text = "billing"\npassed = true')

    errors = checked(with_prompt(tmp_path, lying)).errors

    assert any("sample 2 on a/one@p1: the check says False" in line for line in errors)


def test_reverify_samples_each_side_and_records_the_check(database, monkeypatch, tmp_path):
    """Each answer is in the call log, and the file names its call."""
    connected(database, monkeypatch)
    base = with_prompt(tmp_path, samples=None)
    answers = ["bug", "other", "billing", "other"]
    client = FakeTransport.per_deployment({("a/one", "p1"): [Verdict(text=t) for t in answers]})

    run_cli(
        monkeypatch, "module", "reverify", base.name, "--content", str(base.parent), client=client
    )

    held = tomllib.loads((base / "samples" / "jdg-label.toml").read_text())
    assert [(s["side"], s["text"], s["passed"]) for s in held["sample"]] == [
        ("clean", "other", True),
        ("clean", "bug", False),
        ("no-other", "billing", False),
        ("no-other", "other", True),
    ]
    assert [(c["holds"], c["measured"]) for c in held["checks"]] == [
        (True, "clean 1 of 2 passed; no-other 1 of 2 failed")
    ]
    calls = {c.id for c in CallLog(database).all()}
    assert {s["call"] for s in held["sample"]} <= calls
    assert checked(base).errors == []
