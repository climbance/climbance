import tomllib
from datetime import date
from pathlib import Path

import pytest
from commands import connected, run_cli
from helpers import FakeTransport, Verdict

from climb.calls import CallLog
from climb.knowledge.authoring.course import load
from climb.knowledge.authoring.reverify import Check, appended, owed, witnessed

PANEL = '[models]\npanel = ["a/one@p1", "b/two@p2"]\nevery_days = 90\n'
WITNESS = """
said = ask(model, "Say yes or no.")
print(f"answered {said}")
print("holds" if said == "yes" else "fails")
"""
CONCEPTS = f"""# a header comment

[[concept]]
id = "first"
level = 0
witness = '''
print("x")
'''
output = '''
[0] a line opening like a table
'''

[[concept]]
id = "lost-middle"
level = 1
model_witness = '''{WITNESS}'''

[[concept.checks]]
model = "a/one@p1"
checked_on = 2026-01-02
holds = true
measured = "answered yes"

# --- Level 2 ---

[[concept]]
id = "last"
level = 2
"""


def module(tmp_path: Path, concepts: str = CONCEPTS) -> Path:
    root = tmp_path / "modules" / "m"
    (root / "concepts" / "t").mkdir(parents=True)
    (root / "course.toml").write_text('title = "M"\n')
    (root / "graph.toml").write_text("")
    (root / "check.toml").write_text(PANEL)
    (root / "concepts" / "t" / "sub.toml").write_text(concepts)
    return root


def test_a_claim_is_owed_on_each_model_unchecked_or_past_the_period(tmp_path):
    """Rule 31: a model with no check, or one past `every_days`, is due."""
    course = load(module(tmp_path))

    assert owed(course, date(2026, 2, 1)) == {"lost-middle": ["b/two@p2"]}
    assert owed(course, date(2026, 6, 1)) == {"lost-middle": ["a/one@p1", "b/two@p2"]}


def test_a_failed_latest_check_is_not_owed_again(tmp_path):
    """Rule 31: a claim that stopped holding is retired, not run again."""
    failed = CONCEPTS.replace("holds = true", "holds = false")

    assert owed(load(module(tmp_path, failed)), date(2026, 6, 1)) == {"lost-middle": ["b/two@p2"]}


def test_the_witness_reads_its_verdict_and_measurement_from_the_last_lines():
    """The run gives the witness `ask` and the `model` it is checking."""
    asked = []

    def ask(model: str, prompt: str) -> str:
        asked.append((model, prompt))
        return "no"

    assert witnessed(WITNESS, "b/two@p2", ask) == (False, "answered no")
    assert asked == [("b/two@p2", "Say yes or no.")]


def test_a_witness_printing_no_verdict_is_refused():
    """A missing verdict is no check: nothing is appended for it."""
    with pytest.raises(ValueError, match="verdict"):
        witnessed("print('0.6 against 0.8')\n", "a/one@p1", lambda _m, _p: "")


def test_checks_are_appended_to_their_concept_and_nothing_else_moves(tmp_path):
    """A check is appended, never edited, and the comment before the next
    concept stays with that concept."""
    path = module(tmp_path) / "concepts" / "t" / "sub.toml"
    on = date(2026, 11, 27)

    appended(path, [Check("lost-middle", "b/two@p2", on, False, 'answered "no" é')])

    text = path.read_text()
    assert text.startswith(CONCEPTS.split("\n# --- Level 2")[0])
    assert text.endswith(
        'measured = "answered \\"no\\" \\u00e9"\n\n# --- Level 2 ---\n\n'
        '[[concept]]\nid = "last"\nlevel = 2\n'
    )
    (_, middle, last) = tomllib.loads(text)["concept"]
    assert middle["checks"][1] == {
        "model": "b/two@p2",
        "checked_on": on,
        "holds": False,
        "measured": 'answered "no" é',
    }
    assert "checks" not in last


def test_checks_written_inline_are_refused_and_the_file_kept(tmp_path):
    """`[[concept.checks]]` cannot follow an inline `checks` array."""
    inline = CONCEPTS.replace("level = 1\n", "level = 1\nchecks = []\n").replace(
        '[[concept.checks]]\nmodel = "a/one@p1"\nchecked_on = 2026-01-02\nholds = true\n'
        'measured = "answered yes"\n',
        "",
    )
    path = module(tmp_path, inline) / "concepts" / "t" / "sub.toml"

    with pytest.raises(ValueError, match=r"\[\[concept.checks\]\]"):
        appended(path, [Check("lost-middle", "a/one@p1", date(2026, 11, 27), True, "yes")])
    assert path.read_text() == inline


def test_the_command_appends_a_check_per_due_model_each_call_logged(
    database, monkeypatch, tmp_path, capsys
):
    """Each due panel model gets a check, and each call is in the call log."""
    connected(database, monkeypatch)
    root = module(tmp_path)
    client = FakeTransport.per_deployment(
        {("a/one", "p1"): Verdict(text="yes"), ("b/two", "p2"): Verdict(text="no")}
    )

    run_cli(monkeypatch, "module", "reverify", "m", "--content", str(root.parent), client=client)

    checks = tomllib.loads((root / "concepts" / "t" / "sub.toml").read_text())["concept"][1]
    assert [(c["model"], c["holds"]) for c in checks["checks"][1:]] == [
        ("a/one@p1", True),
        ("b/two@p2", False),
    ]
    calls = [c for c in CallLog(database).all() if c.pin in {"p1", "p2"}]
    assert [(c.model, c.pin, c.effort) for c in calls] == [
        ("a/one", "p1", "default"),
        ("b/two", "p2", "default"),
    ]
    assert "lost-middle on b/two@p2: fails, answered no" in capsys.readouterr().out


def test_a_panel_on_the_subscriptions_runs_through_the_installed_clis(
    database, monkeypatch, tmp_path, capsys
):
    """A bare backend resolves to the installed CLI, and a Codex check says
    it was made through Codex's agent wrapper."""
    connected(database, monkeypatch)
    root = module(tmp_path)
    (root / "check.toml").write_text(
        '[models]\npanel = ["a/one@claude-code", "b/two@codex-cli"]\nevery_days = 90\n'
    )
    client = FakeTransport.per_deployment(
        {
            ("a/one", "claude-code 1.0.0"): Verdict(text="yes"),
            ("b/two", "codex-cli 1.0.0"): Verdict(text="yes"),
        }
    )

    run_cli(monkeypatch, "module", "reverify", "m", "--content", str(root.parent), client=client)

    checks = tomllib.loads((root / "concepts" / "t" / "sub.toml").read_text())["concept"][1]
    assert [(c["model"], c["measured"]) for c in checks["checks"][1:]] == [
        ("a/one@claude-code", "answered yes"),
        ("b/two@codex-cli", "answered yes (through codex exec's agent wrapper)"),
    ]
