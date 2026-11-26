import json
from datetime import date
from pathlib import Path

from authoring import found, shelved, written

from climb.knowledge.authoring import check
from climb.knowledge.authoring.course import Report, load
from climb.knowledge.authoring.model_checks import checked

URL = "https://docs.python.org/3/reference/compound_stmts.html#the-while-statement"
LESSON = "## While\n\n`while` tests its condition first.\n"


def concept(**fields) -> dict:
    return {
        "id": "while-retests",
        "level": 0,
        "claim": "`while` tests its condition before every iteration.",
        "source": URL,
        "witness": "n = 0\nwhile n > 0:\n    print('body')\nprint('done')\n",
        "output": "done\n",
        "misconceptions": [{"id": "body-runs-once", "text": "A `while` body always runs once."}],
        "taught_by": "les#while",
    } | fields


def asking(name: str = "while-retests") -> dict:
    return {
        "id": "w",
        "kind": "concept",
        "concept": name,
        "prompt": "How often does the body run?",
        "choices": ["never", "once", "twice"],
        "answer": ["A"],
        "explain": "The condition is false first.",
        "why": ["a", "b", "c"],
        "misconception": {"B": "body-runs-once", "C": "body-runs-once"},
    }


def module(tmp_path: Path, *concepts: dict, lesson: str = LESSON, q: dict | None = None) -> Path:
    root = written(tmp_path, [q or asking()], lessons={"les": (["sub@0"], lesson)}, coverage="")
    page = "[#the-while-statement]\nThe while\nstatement. A sentence."
    shelved(tmp_path, URL, "2026-11-10", page)
    (root / "concepts" / "t").mkdir(parents=True)
    body = ""
    for one in concepts or (concept(),):
        body += "[[concept]]\n" + "".join(f"{k} = {_toml(v)}\n" for k, v in one.items())
    (root / "concepts" / "t" / "sub.toml").write_text(body)
    return root


def _toml(value) -> str:
    if isinstance(value, dict):
        return "{ " + ", ".join(f"{k} = {_toml(v)}" for k, v in value.items()) + " }"
    if isinstance(value, list):
        return "[" + ", ".join(_toml(v) for v in value) + "]"
    if isinstance(value, date):
        return value.isoformat()
    return json.dumps(value)


def test_a_module_written_by_concept_holding_every_rule_reports_nothing(tmp_path):
    """The fixture breaks no rule, so each finding below is its test's own."""
    report = check(module(tmp_path), other_versions=False).report

    assert (report.errors, report.warnings) == ([], [])


def test_a_witness_printing_another_output_is_refused(tmp_path):
    """Rule 26: the claim rests on what the witness prints."""
    root = module(tmp_path, concept(output="body\ndone\n"))

    errors = found(check(root, other_versions=False).report.errors, 26)

    assert errors == [
        "[26] concepts/t/sub.toml while-retests: witness prints 'done' on the project's "
        "interpreter, where the concept shows 'body\\ndone'"
    ]


def test_a_concept_with_neither_a_witness_nor_a_quote_is_refused(tmp_path):
    """Rule 27: a claim nothing checks."""
    bare = {k: v for k, v in concept().items() if k not in ("witness", "output")}

    errors = found(check(module(tmp_path, bare), run=False).report.errors, 27)

    assert errors == ["[27] concepts/t/sub.toml while-retests: neither a witness nor a quote"]


def test_a_quote_with_no_read_on_date_is_refused(tmp_path):
    """Rule 27: a source page changes after it is quoted."""
    quoted = {k: v for k, v in concept().items() if k not in ("witness", "output")}
    quoted["quote"] = "A sentence."

    errors = found(check(module(tmp_path, quoted), run=False).report.errors, 27)

    assert errors == ["[27] concepts/t/sub.toml while-retests: a quote with no read_on date"]


def test_a_quote_with_its_read_on_date_is_accepted(tmp_path):
    """Rule 27: a TOML date names when the quoted source was read."""
    quoted = {k: v for k, v in concept().items() if k not in ("witness", "output")}
    quoted |= {"quote": "A sentence.", "read_on": date(2026, 11, 15)}

    errors = found(check(module(tmp_path, quoted), run=False).report.errors, 27)

    assert errors == []


def empty(root: Path, *entries: str) -> Path:
    path = root / "concepts" / "t" / "sub.toml"
    path.write_text(path.read_text() + "".join(f"[[empty]]\n{e}\n" for e in entries))
    return root


def test_a_level_recorded_as_empty_with_its_reason_is_accepted(tmp_path):
    """Rule 27: a subtopic may hold no concept at a level, saying why."""
    root = empty(module(tmp_path), 'level = 3\nreason = "Nothing at this depth."')

    assert found(check(root, run=False).report.errors, 27) == []


def test_an_empty_level_is_refused_without_a_reason_or_beside_a_concept(tmp_path):
    """Rule 27: an empty level states why, and holds no concept."""
    entries = ("level = 0", 'level = 2\nreason = " "', 'level = 2\nreason = "x"')
    root = empty(module(tmp_path), *entries)

    assert found(check(root, run=False).report.errors, 27) == [
        "[27] concepts/t/sub.toml empty L0: no reason",
        "[27] concepts/t/sub.toml empty L0: the file holds a concept at this level",
        "[27] concepts/t/sub.toml empty L2: no reason",
        "[27] concepts/t/sub.toml empty L2: recorded twice",
    ]


def test_a_question_naming_an_unknown_concept_is_refused(tmp_path):
    """Rule 27: the reading's own finding, reported by the check."""
    errors = found(check(module(tmp_path, q=asking("nope")), run=False).report.errors, 27)

    assert errors == ["[27] banks/t/sub.toml:w: unknown concept nope"]


def test_a_lesson_section_teaching_no_concept_is_refused(tmp_path):
    """Rule 28: a section asserting what no witness checks."""
    root = module(tmp_path, lesson=LESSON + "\n## Loops\n\nMore.\n")

    errors = found(check(root, run=False).report.errors, 28)

    assert errors == ["[28] lessons/les.md: #loops teaches no concept"]


def test_a_hand_written_intro_or_mistakes_section_is_refused(tmp_path):
    """Rule 28: the seed renders both, and a copy drifts."""
    root = module(tmp_path, lesson="Loops repeat.\n\n" + LESSON + "\n## Common mistakes\n\n- x\n")

    errors = found(check(root, run=False).report.errors, 28)

    assert any("holds an intro" in e for e in errors)
    assert any("#common-mistakes" in e for e in errors)


def test_a_taught_by_naming_no_section_is_refused(tmp_path):
    """Rule 28: a concept no lesson teaches."""
    root = module(tmp_path, concept(taught_by="les#until"))

    errors = found(check(root, run=False).report.errors, 28)

    assert any("taught_by les#until names no section" in e for e in errors)


def test_a_sentence_opening_with_both_is_warned(tmp_path):
    """Rule 29: an opener the writing rules forbid."""
    root = module(tmp_path, concept(claim="Both loops test first. They stop on false."))

    warnings = found(check(root, run=False).report.warnings, 29)

    assert any("opens with 'Both'" in w for w in warnings)


def test_a_question_naming_no_concept_is_refused_where_concepts_file_questions(tmp_path):
    """Rule 19: in a module written by concept, a question is filed by its
    concept, and the coverage map is not read."""
    loose = asking() | {"lesson": "les#while", "level": 0, "detail": {"mechanism": "Tests first."}}
    del loose["concept"]

    errors = found(check(module(tmp_path, q=loose), run=False).report.errors, 19)

    assert errors == ["[19] banks/t/sub.toml w: names no concept"]


def test_a_misconception_no_wrong_choice_embodies_is_warned(tmp_path):
    """Rule 19: a known wrong belief no question tests."""
    second = {"id": "stops-mid-body", "text": "A `while` loop stops mid-body."}
    root = module(tmp_path, concept(misconceptions=[*concept()["misconceptions"], second]))

    warnings = found(check(root, run=False).report.warnings, 19)

    assert any("misconception stops-mid-body" in w for w in warnings)


def test_a_keyed_choice_naming_a_misconception_is_refused(tmp_path):
    """Rule 19: the right answer embodies no wrong belief."""
    q = asking() | {"misconception": {"A": "body-runs-once", "B": "body-runs-once"}}

    errors = found(check(module(tmp_path, q=q), run=False).report.errors, 19)

    assert any("keyed choice A names a misconception" in e for e in errors)


def test_two_misconceptions_sharing_an_id_are_refused(tmp_path):
    """Rule 27: a choice naming the id could mean either belief."""
    twice = [{"id": "x", "text": "One."}, {"id": "x", "text": "Two."}]

    errors = found(
        check(module(tmp_path, concept(misconceptions=twice)), run=False).report.errors, 27
    )

    assert any("share an id" in e for e in errors)


def test_a_short_reply_of_only_true_or_false_is_refused(tmp_path):
    """Rule 3: a reply with even odds is guessed, not recalled."""
    q = {k: v for k, v in asking().items() if k not in ("choices", "answer", "why")}
    q |= {"format": "short", "accept": ["True", "true"]}
    del q["misconception"]

    errors = found(check(module(tmp_path, q=q), run=False).report.errors, 3)

    assert errors == ["[3] banks/t/sub.toml w: the reply is a yes or no, so the format is choice"]


def test_a_question_sharing_a_name_with_its_section_is_warned(tmp_path):
    """Rule 15: a renamed copy keeps a name of the section's example."""
    lesson = "## While\n\n```python\nfuel = 7\nwhile fuel > 4:\n    fuel = fuel - 1\n```\n"
    q = asking() | {"kind": "output", "code": "fuel = 9\nprint(fuel > 4, 'start')\n"}

    warnings = found(check(module(tmp_path, lesson=lesson, q=q), run=False).report.warnings, 15)

    assert warnings == ["[15] banks/t/sub.toml w: shares fuel with les#while"]


def test_a_keyword_argument_or_a_builtin_shared_with_the_section_is_not_warned(tmp_path):
    """Rule 15: `start=` and `enumerate` are the API the section teaches."""
    lesson = "## While\n\n```python\nfor i, w in enumerate(ws, start=1):\n    print(i)\n```\n"
    q = asking() | {"kind": "output", "code": "print(list(enumerate('ab', start=5)))\n"}

    warnings = found(check(module(tmp_path, lesson=lesson, q=q), run=False).report.warnings, 15)

    assert warnings == []


def test_a_why_opening_with_its_verdict_is_warned(tmp_path):
    """Rule 12: the client marks each choice, so `Wrong:` repeats the mark."""
    q = asking() | {"why": ["Right: a", "b", "c"]}

    warnings = found(check(module(tmp_path, q=q), run=False).report.warnings, 12)

    assert warnings == [
        "[12] banks/t/sub.toml w: a why opens with its verdict, which the client shows"
    ]


def test_a_question_line_over_40_characters_is_warned(tmp_path):
    """Rule 25: a phone wraps a question's line of 44 characters."""
    q = asking() | {"kind": "output", "code": f"print({'1' * 40})\n"}

    warnings = found(check(module(tmp_path, q=q), run=False).report.warnings, 25)

    assert warnings == ["[25] banks/t/sub.toml w code: 1 line over 40 characters, the longest 47"]


def test_a_snippet_over_12_lines_is_warned(tmp_path):
    """Rule 25: a task grown past what one claim needs."""
    q = asking() | {"kind": "output", "code": "x = 1\n" * 13}

    warnings = found(check(module(tmp_path, q=q), run=False).report.warnings, 25)

    assert warnings == ["[25] banks/t/sub.toml w code: 13 lines, over 12"]


def test_another_concepts_misconception_counts_as_embodied(tmp_path):
    """Rule 19: a choice naming `concept#id` covers that concept's belief."""
    other = concept(
        id="until-stops", taught_by="les#while", misconceptions=[{"id": "x", "text": "X."}]
    )
    q = asking() | {"misconception": {"B": "body-runs-once", "C": "until-stops#x"}}

    warnings = found(check(module(tmp_path, concept(), other, q=q), run=False).report.warnings, 19)

    assert not any("misconception x" in w for w in warnings)


def test_a_question_the_seed_would_refuse_is_refused(tmp_path):
    """A module the check passes is one the seed takes, derived fields too."""
    many = [{"id": f"m{i}", "text": f"Belief {i}."} for i in range(7)]
    q = asking() | {"misconception": {"B": "m0", "C": "m1"}}

    errors = check(module(tmp_path, concept(misconceptions=many), q=q), run=False).report.errors

    assert any(e.startswith("[0] seed: ") and "pitfalls" in e for e in errors)


def test_a_key_every_distractor_varies_by_one_part_is_warned(tmp_path):
    """Rule 10: the key sits at the centre, and the choices alone give it."""
    choices = ["True True", "False True", "True False"]
    q = asking() | {"choices": choices, "why": ["a", "b", "c"]}

    warnings = found(check(module(tmp_path, q=q), run=False).report.warnings, 10)

    assert any("shares a part with every other choice" in w for w in warnings)


def test_choices_sharing_parts_evenly_are_not_warned(tmp_path):
    """Rule 10: two distractors sharing a part the key lacks hide the key."""
    choices = ["True True", "False True", "False False"]
    q = asking() | {"choices": choices, "why": ["a", "b", "c"]}

    warnings = found(check(module(tmp_path, q=q), run=False).report.warnings, 10)

    assert not any("shares a part" in w for w in warnings)


def test_a_centred_key_among_tuples_is_warned(tmp_path):
    """Rule 10: a tuple's items are its parts, as a choice's words are."""
    choices = ["(2, None)", "(2, 'b')", "(0, None)"]
    q = asking() | {"choices": choices, "why": ["a", "b", "c"]}

    warnings = found(check(module(tmp_path, q=q), run=False).report.warnings, 10)

    assert any("shares a part with every other choice" in w for w in warnings)


def quoting(quote: str, **fields) -> dict:
    bare = {k: v for k, v in concept().items() if k not in ("witness", "output")}
    return bare | {"quote": quote, "read_on": date(2026, 11, 15)} | fields


def test_a_quote_in_its_snapshot_whitespace_aside_is_accepted(tmp_path):
    """Rule 30: the text breaks lines the quote does not, and marks anchors."""
    root = module(tmp_path, quoting("The while statement."))

    assert found(check(root, run=False).report.errors, 30) == []


def test_a_source_the_library_holds_no_snapshot_of_is_refused(tmp_path):
    """Rule 30: a source never fetched gives the review nothing to read."""
    url = "https://docs.python.org/3/library/sys.html#sys.exit"
    root = module(tmp_path, concept(source=[URL, url]))

    errors = found(check(root, run=False).report.errors, 30)

    assert errors == [f"[30] concepts/t/sub.toml while-retests: no snapshot of {url}"]


def test_a_quote_only_a_later_snapshot_holds_is_refused(tmp_path):
    """Rule 30: `read_on` names the latest snapshot fetched by that date."""
    shelved(tmp_path, URL, "2026-11-20", "[#the-while-statement]\nA new sentence.")
    root = module(tmp_path, quoting("A new sentence."))

    errors = found(check(root, run=False).report.errors, 30)

    assert errors == [
        "[30] concepts/t/sub.toml while-retests: no snapshot it cites holds the quote "
        "'A new sentence.'"
    ]


def test_an_anchor_the_snapshot_does_not_hold_is_refused(tmp_path):
    """Rule 30: a renamed section leaves the link pointing at the page's top."""
    url = URL.replace("#the-while-statement", "#the-for-statement")
    root = module(tmp_path, concept(source=url))

    errors = found(check(root, run=False).report.errors, 30)

    assert errors == [
        f"[30] concepts/t/sub.toml while-retests: snapshot 2026-11-10 of {url} "
        "holds no #the-for-statement"
    ]


def test_a_quote_beside_a_source_kept_outside_git_is_refused(tmp_path):
    """Rule 30: a review cannot read a Wikipedia snapshot from git."""
    wiki = "https://en.wikipedia.org/wiki/While_loop#Overview"
    root = module(tmp_path, quoting("A sentence.", source=[URL, wiki]))

    errors = found(check(root, run=False).report.errors, 30)

    assert errors == [
        f"[30] concepts/t/sub.toml while-retests: quotes beside {wiki}, which git does not hold"
    ]


def test_an_elided_quote_matches_its_parts_in_order(tmp_path):
    """Rule 30: `[...]` stands for skipped text, never for a reordering."""
    kept = module(tmp_path / "a", quoting("The while [...] A sentence."))
    swapped = module(tmp_path / "b", quoting("A sentence. [...] The while"))

    assert found(check(kept, run=False).report.errors, 30) == []
    assert len(found(check(swapped, run=False).report.errors, 30)) == 1


MODEL = {
    "model_witness": "print('holds')\n",
    "quote": "A sentence.",
    "read_on": date(2026, 11, 15),
}
PANEL = '[models]\npanel = ["a/one", "b/two"]\nevery_days = 90\n'


def held(model: str, on: date, holds: bool = True) -> dict:
    return {"model": model, "checked_on": on, "holds": holds, "measured": "0.6 against 0.8"}


def checking(tmp_path: Path, *checks: dict, config: str = PANEL, **fields) -> list[str]:
    root = module(tmp_path, concept(**MODEL, checks=list(checks), **fields))
    (root / "check.toml").write_text(config)
    course = load(root)
    report = Report()
    checked(course, report, today=date(2026, 12, 1))
    return report.errors + report.warnings


def test_a_claim_checked_on_every_panel_model_lately_reports_nothing(tmp_path):
    """Rule 31: the latest check on each panel model held, within the period."""
    on = date(2026, 11, 20)

    assert checking(tmp_path, held("a/one", on), held("b/two", on)) == []


def test_a_claim_whose_latest_check_failed_must_be_retired(tmp_path):
    """Rule 31: a claim that stopped holding on one panel model is false."""
    checks = (held("a/one", date(2026, 9, 1)), held("a/one", date(2026, 11, 20), holds=False))

    assert checking(tmp_path, *checks, held("b/two", date(2026, 11, 20))) == [
        "[31] concepts/t/sub.toml while-retests: stopped holding on a/one on 2026-11-20: retire it"
    ]


def test_a_claim_unchecked_on_a_model_or_past_its_period_is_due(tmp_path):
    """Rule 31: a new panel model, or a check past the period, is due."""
    assert checking(tmp_path, held("a/one", date(2026, 8, 1))) == [
        "[31] concepts/t/sub.toml while-retests: due: last checked on a/one on 2026-08-01",
        "[31] concepts/t/sub.toml while-retests: due: never checked on b/two",
    ]


def test_a_model_witness_in_a_module_naming_no_panel_is_refused(tmp_path):
    """Rule 31: with no panel, the claim's checks name models nobody chose."""
    assert checking(tmp_path, held("a/one", date(2026, 11, 20)), config="") == [
        "[31] concepts/t/sub.toml while-retests: check.toml names no [models] panel and every_days"
    ]


def test_a_malformed_check_is_refused(tmp_path):
    """Rule 31: a check names its model, date, verdict and measurement."""
    bare = {"model": "a/one", "checked_on": date(2026, 11, 20)}

    assert checking(
        tmp_path, bare, held("a/one", date(2026, 11, 20)), held("b/two", date(2026, 11, 20))
    )[0] == (
        "[31] concepts/t/sub.toml while-retests: a check is not "
        "{ model, checked_on, holds, measured }"
    )


def test_a_retired_id_is_refused_and_its_entry_needs_a_reason(tmp_path):
    """Rule 31: a retired id is never reused, and its retirement says why."""
    on = date(2026, 11, 20)
    config = PANEL + "[retired.while-retests]\nretired_on = 2026-11-01\n"

    assert checking(tmp_path, held("a/one", on), held("b/two", on), config=config) == [
        "[31] concepts/t/sub.toml while-retests: the id was retired",
        "[31] check.toml retired while-retests: needs retired_on and because",
    ]
